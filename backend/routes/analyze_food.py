"""
Food Analysis API Routes

Main endpoint for analyzing food ingredients.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.intent_inference import intent_engine
from ai.reasoning_engine import reasoning_engine
from ai.explanation_generator import explanation_generator
from ai.deception_detector import deception_detector
from ai.nutrition_analyzer import NutritionAnalyzer, NutritionData
from ai.vision_extractor import VisionIngredientExtractor
from utils.ingredient_parser import smart_ingredient_split
import google.generativeai as genai
import re

router = APIRouter()

# Initialize nutrition analyzer
nutrition_analyzer = NutritionAnalyzer()


class AnalyzeRequest(BaseModel):
    """Request model for food analysis."""
    ingredients: List[str]
    product_name: Optional[str] = None
    user_question: Optional[str] = None
    include_eli5: bool = False
    user_preferences: Optional[List[str]] = None  # Session-based preferences
    language: Optional[str] = "en"  # Language code (en, hi, bn, ta, etc.)
    # NEW: Support nutrition analysis
    analysis_type: Optional[str] = "ingredients"  # "ingredients" | "nutrition" | "both"
    nutrition_image: Optional[str] = None  # Base64 image for nutrition extraction


class AnalyzeResponse(BaseModel):
    """Response model for food analysis."""
    status: str
    data: dict


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_food(request: AnalyzeRequest):
    """
    Analyze food ingredients and/or nutrition facts.
    
    This is the CORE ENDPOINT that powers the entire experience.
    
    Supports 3 modes:
    - "ingredients": Analyze ingredient list (existing flow)
    - "nutrition": Analyze nutrition facts from image
    - "both": Combined analysis (ingredients + nutrition)
    
    Pipeline:
    1. Intent Inference
    2. Reasoning Engine / Nutrition Analysis
    3. Explanation Generation
    """
    try:
        # Initialize response data
        response_data = {}
        
        # ==================== NUTRITION ANALYSIS MODE ====================
        if request.analysis_type in ["nutrition", "both"] and request.nutrition_image:
            print("📊 Nutrition analysis mode activated")
            
            # Extract nutrition from image
            nutrition_result = await extract_nutrition_from_image(request.nutrition_image)
            
            # Add to response
            response_data["nutrition_analysis"] = nutrition_result["analysis"]
            response_data["nutrition_data"] = nutrition_result["nutrition_data"]
        
        # ==================== INGREDIENTS ANALYSIS MODE ====================
        if request.analysis_type in ["ingredients", "both"]:
            # Validate input
            if not request.ingredients or len(request.ingredients) == 0:
                raise HTTPException(
                    status_code=400,
                    detail="At least one ingredient is required"
                )
            
            # Smart parsing: handle commas inside parentheses
            if len(request.ingredients) == 1 and ',' in request.ingredients[0]:
                parsed_ingredients = smart_ingredient_split(request.ingredients[0])
                print(f"📝 Smart parsing: {len(request.ingredients)} → {len(parsed_ingredients)} ingredients")
                print(f"   Original: {request.ingredients[0][:100]}...")
                print(f"   Parsed: {parsed_ingredients[:5]}...")
                request.ingredients = parsed_ingredients
            
            print(f"🔍 Analyzing {len(request.ingredients)} ingredients")
            
            # Step 1: Infer user intent
            intent_result = intent_engine.analyze(
                ingredients=request.ingredients,
                product_name=request.product_name,
                user_question=request.user_question
            )
            
            # INNOVATION: Apply user preferences if provided
            if request.user_preferences:
                intent_result["personalized_hints"] = request.user_preferences
            
            # Step 2: Detect deceptive ingredients (PATENT FEATURE)
            deception_alerts = deception_detector.detect_deceptions(request.ingredients)
            overall_deception_score = deception_detector.get_overall_deception_score(deception_alerts)
            
            # Step 3: Run reasoning engine
            reasoning_result = reasoning_engine.analyze_ingredients(
                ingredients=request.ingredients,
                intent=intent_result["primary_intent"],
                food_context=intent_result["food_context"]
            )
            
            # Convert to dict for JSON serialization
            reasoning_dict = {
                "overall_signal": reasoning_result.overall_signal,
                "overall_confidence": reasoning_result.overall_confidence,
                "insights": [insight.dict() for insight in reasoning_result.insights],
                "trade_offs": reasoning_result.trade_offs,
                "uncertainty_note": reasoning_result.uncertainty_note
            }
            
            # Step 4: Generate explanations (pass ALL ingredients for comprehensive AI analysis)
            explanation_result = explanation_generator.generate_complete_explanation(
                reasoning_result=reasoning_dict,
                intent_result=intent_result,
                include_eli5=request.include_eli5,
                language=request.language or "en",
                original_ingredients=request.ingredients  # Pass ALL ingredients for AI analysis
            )
            
            # Add ingredients analysis to response
            response_data.update({
                # Context
                "context": {
                    "food_type": intent_result["food_context"],
                    "detected_intent": intent_result["primary_intent"],
                    "summary": explanation_result.summary
                },
                
                # Core insights (top priority)
                "insights": reasoning_dict["insights"],
                
                # COMPREHENSIVE DETAILED ANALYSIS - ALL ingredients analyzed by AI
                "detailed_insights": explanation_result.detailed_insights,
                
                # Overall health signal
                "health_signal": {
                    "level": reasoning_dict["overall_signal"],
                    "confidence": reasoning_dict["overall_confidence"],
                    "icon": _get_signal_icon(reasoning_dict["overall_signal"])
                },
                
                # Trade-offs
                "trade_offs": reasoning_dict["trade_offs"],
                
                # Uncertainty communication
                "uncertainty_note": reasoning_dict["uncertainty_note"],
                
                # ELI5 explanation (if requested)
                "eli5_explanation": explanation_result.eli5_explanation,
                
                # AI-generated follow-ups
                "follow_up_questions": [
                    fq.dict() for fq in explanation_result.follow_up_questions
                ],
                
                # PATENT FEATURE: Deception detection results
                "deception_analysis": {
                    "overall_score": overall_deception_score,
                    "alerts": [alert.dict() for alert in deception_alerts],
                    "alert_count": len(deception_alerts)
                }
            })
        
        return AnalyzeResponse(
            status="success",
            data=response_data
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@router.post("/analyze/eli5")
async def get_eli5_explanation(request: AnalyzeRequest):
    """
    Get ELI5 (Explain Like I'm 5) version of analysis.
    
    Separate endpoint for on-demand simplification.
    """
    # Set include_eli5 to True
    request.include_eli5 = True
    
    # Reuse main analyze endpoint
    result = await analyze_food(request)
    
    # Return only ELI5 portion
    return {
        "status": "success",
        "eli5_explanation": result.data.get("eli5_explanation")
    }


@router.get("/demo-products")
async def get_demo_products():
    """
    Return pre-configured demo products for testing.
    
    Useful for hackathon demo when you don't have real products.
    """
    demo_products = [
        {
            "id": 1,
            "name": "Sugar Blast Cereal",
            "category": "Breakfast Cereal",
            "ingredients": [
                "sugar",
                "corn syrup",
                "wheat flour",
                "red 40",
                "yellow 5",
                "bht",
                "salt"
            ],
            "image_url": "/demo/cereal.jpg"
        },
        {
            "id": 2,
            "name": "Energy Cola",
            "category": "Beverage",
            "ingredients": [
                "carbonated water",
                "high fructose corn syrup",
                "caffeine",
                "sodium benzoate",
                "aspartame",
                "red 40"
            ],
            "image_url": "/demo/soda.jpg"
        },
        {
            "id": 3,
            "name": "Protein Power Bar",
            "category": "Snack",
            "ingredients": [
                "whey protein",
                "oats",
                "honey",
                "almonds",
                "dark chocolate",
                "soy lecithin",
                "salt"
            ],
            "image_url": "/demo/protein-bar.jpg"
        },
        {
            "id": 4,
            "name": "Cheese Crackers",
            "category": "Snack",
            "ingredients": [
                "enriched flour",
                "vegetable oil",
                "cheese",
                "salt",
                "sugar",
                "soy lecithin",
                "yellow 5",
                "yellow 6"
            ],
            "image_url": "/demo/crackers.jpg"
        },
        {
            "id": 5,
            "name": "Fruit Gummies",
            "category": "Candy",
            "ingredients": [
                "corn syrup",
                "sugar",
                "gelatin",
                "citric acid",
                "red 40",
                "yellow 5",
                "blue 1",
                "natural flavors"
            ],
            "image_url": "/demo/gummies.jpg"
        }
    ]
    
    return {
        "status": "success",
        "products": demo_products
    }


def _get_signal_icon(signal: str) -> str:
    """Helper: Get emoji for health signal."""
    icons = {
        "likely_safe": "🟢",
        "moderate_concern": "🟡",
        "potential_risk": "🔴"
    }
    return icons.get(signal, "⚪")


@router.post("/extract-nutrition")
async def extract_nutrition_from_image(
    image_data: str  # Base64 encoded image
):
    """
    Extract nutrition facts from image using Gemini Vision AI
    
    Args:
        image_data: Base64 encoded image string (with or without data URI prefix)
    
    Returns:
        {
            "status": "success",
            "nutrition_data": {...},
            "analysis": {...},
            "raw_text": "..."
        }
    """
    try:
        import base64
        
        # Remove data URI prefix if present
        if "base64," in image_data:
            image_data = image_data.split("base64,")[1]
        
        # Decode base64 to bytes
        image_bytes = base64.b64decode(image_data)
        
        # Initialize Gemini
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="Gemini API key not configured")
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Prepare image for Gemini
        import PIL.Image
        import io
        image = PIL.Image.open(io.BytesIO(image_bytes))
        
        # Craft nutrition extraction prompt
        prompt = """
You are a nutrition facts extraction expert. Analyze this image and extract the nutrition information from the nutrition facts label/table.

Extract the following values PER SERVING (not per 100g unless that's the only data available):

1. Serving Size (e.g., "50g", "1 cup", "30ml")
2. Servings per Container/Pack
3. Calories (kcal)
4. Protein (g)
5. Carbohydrates (g)
6. Total Sugars (g)
7. Added Sugars (g) - if mentioned separately
8. Total Fat (g)
9. Saturated Fat (g)
10. MUFA Fat (g) - if available
11. PUFA Fat (g) - if available
12. Trans Fat (g)
13. Cholesterol (mg)
14. Sodium (mg)
15. Dietary Fiber (g) - if available

CRITICAL INSTRUCTIONS:
- If the table shows "Per 100g" and "Per Serving" columns, ALWAYS use "Per Serving" values
- Extract EXACT numerical values from the table
- If a value is 0, write "0" not "None"
- If a value is not shown in the table, write "Not listed"
- DO NOT calculate or estimate values
- Pay attention to units (g vs mg)

Return the data in this EXACT JSON format:
{
  "serving_size": "50g",
  "servings_per_pack": 9,
  "per_100g": false,
  "calories": 200.19,
  "protein": 3.58,
  "carbohydrates": 24.59,
  "total_sugars": 16.51,
  "added_sugars": 7.94,
  "total_fat": 9.73,
  "saturated_fat": 5.5,
  "mufa_fat": 3.44,
  "pufa_fat": 0.79,
  "trans_fat": 0,
  "cholesterol": 41.4,
  "sodium": 72.98,
  "dietary_fiber": "Not listed"
}

Return ONLY the JSON, no other text.
"""
        
        # Call Gemini
        response = model.generate_content([prompt, image])
        raw_text = response.text.strip()
        
        print(f"📊 Gemini nutrition extraction response:\n{raw_text}")
        
        # Parse JSON from response
        # Remove markdown code blocks if present
        json_text = raw_text
        if "```json" in json_text:
            json_text = json_text.split("```json")[1].split("```")[0].strip()
        elif "```" in json_text:
            json_text = json_text.split("```")[1].split("```")[0].strip()
        
        import json
        nutrition_dict = json.loads(json_text)
        
        # Helper function to safely convert values
        def safe_float(value):
            """Convert to float, handling 'Not listed' and None"""
            if value is None or value == "Not listed" or value == "":
                return None
            try:
                return float(value)
            except (ValueError, TypeError):
                return None
        
        # Convert to NutritionData object
        nutrition_data = NutritionData(
            serving_size=nutrition_dict.get("serving_size"),
            servings_per_pack=safe_float(nutrition_dict.get("servings_per_pack")),
            calories=safe_float(nutrition_dict.get("calories")),
            protein=safe_float(nutrition_dict.get("protein")),
            carbohydrates=safe_float(nutrition_dict.get("carbohydrates")),
            total_sugars=safe_float(nutrition_dict.get("total_sugars")),
            added_sugars=safe_float(nutrition_dict.get("added_sugars")),
            total_fat=safe_float(nutrition_dict.get("total_fat")),
            saturated_fat=safe_float(nutrition_dict.get("saturated_fat")),
            mufa_fat=safe_float(nutrition_dict.get("mufa_fat")),
            pufa_fat=safe_float(nutrition_dict.get("pufa_fat")),
            trans_fat=safe_float(nutrition_dict.get("trans_fat")),
            cholesterol=safe_float(nutrition_dict.get("cholesterol")),
            sodium=safe_float(nutrition_dict.get("sodium")),
            dietary_fiber=safe_float(nutrition_dict.get("dietary_fiber")),
            per_100g=nutrition_dict.get("per_100g", False)
        )
        
        # Analyze nutrition
        analysis_result = nutrition_analyzer.analyze(nutrition_data)
        
        return {
            "status": "success",
            "nutrition_data": nutrition_dict,
            "analysis": analysis_result,
            "raw_text": raw_text
        }
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        print(f"Raw response: {raw_text}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse nutrition data from image. AI response was not valid JSON. Error: {str(e)}"
        )
    except Exception as e:
        print(f"❌ Nutrition extraction error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract nutrition facts: {str(e)}"
        )

