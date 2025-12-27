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
from utils.ingredient_parser import smart_ingredient_split

router = APIRouter()


class AnalyzeRequest(BaseModel):
    """Request model for food analysis."""
    ingredients: List[str]
    product_name: Optional[str] = None
    user_question: Optional[str] = None
    include_eli5: bool = False
    user_preferences: Optional[List[str]] = None  # Session-based preferences
    language: Optional[str] = "en"  # Language code (en, hi, bn, ta, etc.)


class AnalyzeResponse(BaseModel):
    """Response model for food analysis."""
    status: str
    data: dict


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_food(request: AnalyzeRequest):
    """
    Analyze food ingredients and return AI-native insights.
    
    This is the CORE ENDPOINT that powers the entire experience.
    
    Pipeline:
    1. Intent Inference
    2. Reasoning Engine
    3. Explanation Generation
    """
    try:
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
        
        # Assemble final response
        response_data = {
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
