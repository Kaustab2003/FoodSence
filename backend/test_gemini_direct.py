"""
Direct test of Gemini API to see if it's responding
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# List available models
print("🔍 Listing available Gemini models:\n")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"  ✓ {m.name}")

print("\n" + "="*80 + "\n")

# Use model from env
model_name = os.getenv("AI_MODEL", "gemini-2.0-flash-exp")
model = genai.GenerativeModel(model_name)

print(f"🧪 Testing Gemini API with model: {model_name}\n")

prompt = "Analyze this ingredient in 2 sentences: Sugar"

print(f"📝 Prompt: {prompt}\n")
print("🔄 Calling Gemini...")

try:
    import time
    start = time.time()
    
    response = model.generate_content(prompt)
    
    elapsed = time.time() - start
    
    print(f"✅ Response received in {elapsed:.2f}s\n")
    print(f"📄 Response:\n{response.text}\n")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
