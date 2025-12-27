"""Test Gemini Vision API"""
import os
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
print(f"API Key: {api_key[:20]}...")

try:
    genai.configure(api_key=api_key)
    
    # Try to list models
    print("\nAvailable models:")
    for m in genai.list_models():
        if 'vision' in m.name.lower() or 'generateContent' in str(m.supported_generation_methods):
            print(f"- {m.name}")
    
    # Try gemini-pro-vision
    print("\n\nTesting gemini-pro-vision...")
    model = genai.GenerativeModel('gemini-pro-vision')
    
    # Create a simple test image
    img = Image.new('RGB', (100, 100), color='red')
    
    response = model.generate_content(["What color is this?", img])
    print(f"Response: {response.text}")
    print("✅ Gemini Pro Vision works!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
