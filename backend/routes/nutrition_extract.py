"""
Nutrition Facts Extraction from Images
Uses Vision AI to extract and parse nutrition information from product labels
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import base64
import re

router = APIRouter()


class NutritionImageRequest(BaseModel):
    image: str  # Base64 encoded image
    language: Optional[str] = "en"


@router.post("/extract")
async def extract_nutrition_facts(request: NutritionImageRequest):
    """
    Extract nutrition facts from an image using Vision AI.
    
    Returns parsed nutrition data including:
    - Serving size
    - Calories
    - Macronutrients (protein, carbs, fat)
    - Micronutrients (vitamins, minerals)
    - % Daily Values
    """
    try:
        from ai.vision_extractor import vision_extractor
        
        # Extract text from image using Vision AI
        print(f"🔍 Extracting nutrition facts from image...")
        extracted_text = await vision_extractor.extract_from_base64(
            request.image,
            request.language
        )
        
        print(f"📄 Extracted text: {extracted_text[:200]}...")
        
        # Parse nutrition facts from extracted text
        nutrition_data = parse_nutrition_facts(extracted_text)
        
        return {
            "status": "success",
            "raw_text": extracted_text,
            "nutrition_data": nutrition_data
        }
        
    except Exception as e:
        print(f"❌ Nutrition extraction error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract nutrition facts: {str(e)}"
        )


def parse_nutrition_facts(text: str) -> Dict[str, Any]:
    """
    Parse nutrition facts from extracted text using pattern matching.
    
    Handles various nutrition label formats.
    """
    nutrition = {
        "serving_size": None,
        "servings_per_container": None,
        "calories": None,
        "total_fat": None,
        "saturated_fat": None,
        "trans_fat": None,
        "cholesterol": None,
        "sodium": None,
        "total_carbohydrate": None,
        "dietary_fiber": None,
        "total_sugars": None,
        "added_sugars": None,
        "protein": None,
        "vitamins_minerals": {}
    }
    
    text_lower = text.lower()
    
    # Extract serving size
    serving_match = re.search(r'serving size[:\s]+([0-9.]+\s*(?:g|ml|oz|cup|tbsp|tsp|piece|serving))', text_lower)
    if serving_match:
        nutrition["serving_size"] = serving_match.group(1).strip()
    
    # Extract servings per container
    servings_match = re.search(r'servings per container[:\s]+([0-9.]+)', text_lower)
    if servings_match:
        nutrition["servings_per_container"] = float(servings_match.group(1))
    
    # Extract calories
    calories_match = re.search(r'calories[:\s]+([0-9]+)', text_lower)
    if calories_match:
        nutrition["calories"] = int(calories_match.group(1))
    
    # Extract macronutrients with amounts
    def extract_nutrient(pattern: str, text: str) -> Optional[str]:
        match = re.search(pattern, text)
        return match.group(1).strip() if match else None
    
    nutrition["total_fat"] = extract_nutrient(r'total fat[:\s]+([0-9.]+\s*g)', text_lower)
    nutrition["saturated_fat"] = extract_nutrient(r'saturated fat[:\s]+([0-9.]+\s*g)', text_lower)
    nutrition["trans_fat"] = extract_nutrient(r'trans fat[:\s]+([0-9.]+\s*g)', text_lower)
    nutrition["cholesterol"] = extract_nutrient(r'cholesterol[:\s]+([0-9.]+\s*mg)', text_lower)
    nutrition["sodium"] = extract_nutrient(r'sodium[:\s]+([0-9.]+\s*mg)', text_lower)
    nutrition["total_carbohydrate"] = extract_nutrient(r'total carbohydrate[:\s]+([0-9.]+\s*g)', text_lower)
    nutrition["dietary_fiber"] = extract_nutrient(r'dietary fiber[:\s]+([0-9.]+\s*g)', text_lower)
    nutrition["total_sugars"] = extract_nutrient(r'total sugars[:\s]+([0-9.]+\s*g)', text_lower)
    nutrition["added_sugars"] = extract_nutrient(r'added sugars[:\s]+([0-9.]+\s*g)', text_lower)
    nutrition["protein"] = extract_nutrient(r'protein[:\s]+([0-9.]+\s*g)', text_lower)
    
    # Extract common vitamins and minerals
    vitamins = {
        "vitamin_d": r'vitamin d[:\s]+([0-9.]+\s*(?:mcg|µg|iu))',
        "calcium": r'calcium[:\s]+([0-9.]+\s*mg)',
        "iron": r'iron[:\s]+([0-9.]+\s*mg)',
        "potassium": r'potassium[:\s]+([0-9.]+\s*mg)',
        "vitamin_a": r'vitamin a[:\s]+([0-9.]+\s*(?:mcg|µg|iu))',
        "vitamin_c": r'vitamin c[:\s]+([0-9.]+\s*mg)',
    }
    
    for vitamin_name, pattern in vitamins.items():
        value = extract_nutrient(pattern, text_lower)
        if value:
            nutrition["vitamins_minerals"][vitamin_name] = value
    
    return nutrition
