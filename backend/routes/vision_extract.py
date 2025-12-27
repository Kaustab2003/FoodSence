"""
Vision-based Ingredient Extraction API

Endpoint: POST /api/vision-extract
Accepts: multipart/form-data with image file
Returns: {"ingredients": "...", "model_used": "..."}
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.vision_extractor import vision_extractor

router = APIRouter()


class VisionExtractionResponse(BaseModel):
    """Response model for vision extraction."""
    model_config = {"protected_namespaces": ()}  # Allow 'model_' prefix
    
    ingredients: str
    model_used: str
    confidence: float
    success: bool


@router.post("/vision-extract", response_model=VisionExtractionResponse)
async def extract_from_vision(
    image: UploadFile = File(...),
    language: str = Form("en")
):
    """
    Extract ingredients from food product image using vision models.
    
    Tries in order: Gemini 1.5 Flash → Qwen-VL → LLaVA
    
    Args:
        image: Image file (JPG, PNG, etc.)
        language: Target language code (en, hi, bn, ta, etc.)
    
    Returns:
        VisionExtractionResponse with extracted ingredients
    """
    try:
        # Read image bytes
        image_bytes = await image.read()
        
        # Validate image size (max 10MB)
        if len(image_bytes) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="Image too large (max 10MB)"
            )
        
        # Validate image type
        valid_types = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
        if image.content_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid image type. Supported: {valid_types}"
            )
        
        # Extract using vision models with fallback chain
        result = await vision_extractor.extract(image_bytes, language)
        
        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "All vision models failed")
            )
        
        return VisionExtractionResponse(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Vision extraction failed: {str(e)}"
        )
