"""Test Vision API with a sample image"""
import asyncio
from ai.vision_extractor import vision_extractor
from PIL import Image, ImageDraw, ImageFont
import io

async def test_vision():
    # Create a test image with ingredient text
    img = Image.new('RGB', (600, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    # Add text
    text = "Ingredients: Sugar, Salt, Flour, Butter, Eggs"
    draw.text((20, 80), text, fill='black')
    
    # Convert to bytes
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_bytes = img_byte_arr.getvalue()
    
    print("🧪 Testing Vision API with sample image...")
    print(f"Image size: {len(img_bytes)} bytes")
    
    # Extract ingredients
    result = await vision_extractor.extract(img_bytes, language="en")
    
    print(f"\n✅ Success: {result['success']}")
    print(f"📝 Model used: {result['model_used']}")
    print(f"🎯 Confidence: {result['confidence']}")
    print(f"🥘 Ingredients: {result.get('ingredients', 'None')}")
    
    if not result['success']:
        print(f"❌ Error: {result.get('error', 'Unknown')}")

if __name__ == "__main__":
    asyncio.run(test_vision())
