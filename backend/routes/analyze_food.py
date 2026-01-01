"""
Food Analysis API Routes

Main endpoint for analyzing food ingredients.
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional
from slowapi import Limiter
from slowapi.util import get_remote_address
from functools import lru_cache
import hashlib
import json
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

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize nutrition analyzer
nutrition_analyzer = NutritionAnalyzer()

# In-memory cache for analysis results
_analysis_cache = {}
_cache_max_size = 100

def _get_cached_analysis(ingredients: List[str], language: str) -> Optional[dict]:
    """Get cached analysis result if available."""
    cache_key = hashlib.md5(f"{','.join(sorted(ingredients))}:{language}".encode()).hexdigest()
    return _analysis_cache.get(cache_key)

def _set_cached_analysis(ingredients: List[str], language: str, result: dict):
    """Cache analysis result with LRU eviction."""
    cache_key = hashlib.md5(f"{','.join(sorted(ingredients))}:{language}".encode()).hexdigest()
    
    # LRU eviction: remove oldest entry if cache is full
    if len(_analysis_cache) >= _cache_max_size:
        oldest_key = next(iter(_analysis_cache))
        del _analysis_cache[oldest_key]
    
    _analysis_cache[cache_key] = result


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
@limiter.limit("20/minute")  # Rate limit: 20 requests per minute
async def analyze_food(request: Request, analyze_request: AnalyzeRequest):
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
    
    Rate Limited: 20 requests per minute per IP
    """
    try:
        # Initialize response data
        response_data = {}
        
        # ==================== NUTRITION ANALYSIS MODE ====================
        if analyze_request.analysis_type in ["nutrition", "both"] and analyze_request.nutrition_image:
            print("📊 Nutrition analysis mode activated")
            
            # Extract nutrition from image
            nutrition_result = await extract_nutrition_from_image(analyze_request.nutrition_image)
            
            # Add to response
            response_data["nutrition_analysis"] = nutrition_result["analysis"]
            response_data["nutrition_data"] = nutrition_result["nutrition_data"]
        
        # ==================== INGREDIENTS ANALYSIS MODE ====================
        if analyze_request.analysis_type in ["ingredients", "both"]:
            # Validate input
            if not analyze_request.ingredients or len(analyze_request.ingredients) == 0:
                raise HTTPException(
                    status_code=400,
                    detail="At least one ingredient is required"
                )
            
            # Check cache first
            cached_result = _get_cached_analysis(
                analyze_request.ingredients, 
                analyze_request.language or "en"
            )
            
            if cached_result:
                print(f"✅ Cache hit for {len(analyze_request.ingredients)} ingredients")
                response_data.update(cached_result)
            else:
                print(f"❌ Cache miss - performing full analysis")
                
                # Smart parsing: handle commas inside parentheses
                if len(analyze_request.ingredients) == 1 and ',' in analyze_request.ingredients[0]:
                    parsed_ingredients = smart_ingredient_split(analyze_request.ingredients[0])
                    print(f"📝 Smart parsing: {len(analyze_request.ingredients)} → {len(parsed_ingredients)} ingredients")
                    print(f"   Original: {analyze_request.ingredients[0][:100]}...")
                    print(f"   Parsed: {parsed_ingredients[:5]}...")
                    analyze_request.ingredients = parsed_ingredients
            
                print(f"🔍 Analyzing {len(analyze_request.ingredients)} ingredients")
                
                # Step 1: Infer user intent
                intent_result = intent_engine.analyze(
                    ingredients=analyze_request.ingredients,
                    product_name=analyze_request.product_name,
                    user_question=analyze_request.user_question
                )
                
                # INNOVATION: Apply user preferences if provided
                if analyze_request.user_preferences:
                    intent_result["personalized_hints"] = analyze_request.user_preferences
                
                # Step 2: Detect deceptive ingredients (PATENT FEATURE)
                deception_alerts = deception_detector.detect_deceptions(analyze_request.ingredients)
                overall_deception_score = deception_detector.get_overall_deception_score(deception_alerts)
                
                # Step 3: Run reasoning engine
                reasoning_result = reasoning_engine.analyze_ingredients(
                    ingredients=analyze_request.ingredients,
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
                    include_eli5=analyze_request.include_eli5,
                    language=analyze_request.language or "en",
                    original_ingredients=analyze_request.ingredients  # Pass ALL ingredients for AI analysis
                )
                
                # Build ingredients analysis result
                ingredients_result = {
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
                }
                
                # Cache the result for future requests
                _set_cached_analysis(
                    analyze_request.ingredients,
                    analyze_request.language or "en",
                    ingredients_result
                )
                
                # Add to response
                response_data.update(ingredients_result)
        
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
@limiter.limit("10/minute")  # Rate limit: 10 requests per minute
async def get_eli5_explanation(request: Request, analyze_request: AnalyzeRequest):
    """
    Get ELI5 (Explain Like I'm 5) version of analysis.
    
    Separate endpoint for on-demand simplification.
    Rate Limited: 10 requests per minute per IP
    """
    language = analyze_request.language or "en"
    
    # Check cache first (with eli5 flag in key)
    cache_key_eli5 = hashlib.md5(f"{','.join(sorted(analyze_request.ingredients))}:{language}:eli5".encode()).hexdigest()
    
    if cache_key_eli5 in _analysis_cache:
        print(f"✅ ELI5 Cache hit for {len(analyze_request.ingredients)} ingredients")
        cached_result = _analysis_cache[cache_key_eli5]
        return {
            "status": "success",
            "eli5_explanation": cached_result.get("eli5_explanation")
        }
    
    # Cache miss - generate new analysis with ELI5
    print(f"❌ ELI5 Cache miss - generating for {len(analyze_request.ingredients)} ingredients")
    
    # Get or generate base analysis (without ELI5)
    base_cache_key = hashlib.md5(f"{','.join(sorted(analyze_request.ingredients))}:{language}".encode()).hexdigest()
    
    if base_cache_key in _analysis_cache:
        print(f"✅ Using cached base analysis")
        base_result = _analysis_cache[base_cache_key]
    else:
        # Need to do full analysis first
        print(f"❌ No base analysis cached, performing full analysis")
        analyze_request.include_eli5 = False
        full_result = await analyze_food(request, analyze_request)
        base_result = full_result.data
    
    # Now generate ELI5 from the base analysis
    try:
        from ai.explanation_generator import explanation_generator
        
        # Extract insights and trade-offs from base result
        insights = base_result.get("insights", [])
        trade_offs = base_result.get("trade_offs", {})
        
        print(f"🔍 Generating ELI5 for {len(insights)} insights")
        
        # Generate ELI5
        eli5 = explanation_generator.generate_eli5_explanation(insights, trade_offs)
        
        print(f"✅ ELI5 generated: {len(eli5)} characters")
        
        # Translate if needed
        if language != "en" and eli5:
            eli5 = explanation_generator._translate_text(eli5, language)
        
        # Cache the result
        result_with_eli5 = {**base_result, "eli5_explanation": eli5}
        _analysis_cache[cache_key_eli5] = result_with_eli5
        
        return {
            "status": "success",
            "eli5_explanation": eli5
        }
    except Exception as e:
        print(f"❌ ELI5 generation error: {e}")
        import traceback
        traceback.print_exc()
        return {
            "status": "success",
            "eli5_explanation": "This food has different ingredients. Some are okay, some you should watch out for. It's best to enjoy it sometimes, not all the time!"
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

