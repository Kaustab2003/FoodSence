"""
Barcode Lookup API Route

Fetches product data from Open Food Facts database.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
from typing import Optional

router = APIRouter()


class BarcodeResponse(BaseModel):
    """Product data from barcode scan."""
    product_name: str
    ingredients: str
    found: bool


@router.get("/barcode/{barcode}")
async def lookup_barcode(barcode: str):
    """
    Lookup product by barcode from Open Food Facts.
    
    Args:
        barcode: UPC/EAN barcode number
        
    Returns:
        Product name and ingredients
    """
    try:
        # Query Open Food Facts API
        url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers={
                    "User-Agent": "FoodSenseAI/1.0 (+https://foodsense.ai)"
                },
                timeout=10.0
            )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=404,
                detail=f"Product with barcode {barcode} not found in database"
            )
        
        data = response.json()
        
        # Check if product exists
        if data.get("status") != 1 or not data.get("product"):
            raise HTTPException(
                status_code=404,
                detail="Product not found in Open Food Facts database"
            )
        
        product = data["product"]
        
        # Extract product info
        product_name = (
            product.get("product_name") or 
            product.get("generic_name") or 
            "Unknown Product"
        )
        
        # Try multiple ingredient fields
        ingredients = (
            product.get("ingredients_text") or
            product.get("ingredients_text_en") or
            product.get("ingredients_text_with_allergens") or
            product.get("ingredients_text_with_allergens_en") or
            ""
        )
        
        if not ingredients:
            raise HTTPException(
                status_code=404,
                detail=f"Found product '{product_name}' but no ingredient list available"
            )
        
        return {
            "found": True,
            "product_name": product_name,
            "ingredients": ingredients,
            "barcode": barcode
        }
        
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Request timeout - Open Food Facts API is slow. Try again."
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Network error: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )
