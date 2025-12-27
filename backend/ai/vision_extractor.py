"""
Multi-Model Vision Ingredient Extractor with Fallback Chain

Priority:
1. Gemini Pro Vision (Google) - Fast, accurate, free tier
2. Qwen-VL (HuggingFace Inference API) - Open source fallback
3. LLaVA (HuggingFace Inference API) - Secondary fallback
"""

import os
import base64
from typing import Optional, Dict
from dotenv import load_dotenv

load_dotenv()


class VisionIngredientExtractor:
    """Extract ingredients from images using vision language models."""
    
    def __init__(self):
        self.gemini_api_key = os.getenv("GOOGLE_API_KEY")
        self.hf_api_key = os.getenv("HUGGINGFACE_API_KEY")
        
        # Initialize Gemini
        self.gemini_model = None
        if self.gemini_api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_api_key)
                # Use gemini-2.5-flash (latest stable vision model)
                self.gemini_model = genai.GenerativeModel('gemini-2.5-flash')
                print("✅ Gemini Vision initialized (gemini-2.5-flash)")
            except Exception as e:
                print(f"⚠️ Gemini initialization failed: {e}")
    
    async def extract(self, image_bytes: bytes, language: str = "en") -> Dict:
        """
        Extract ingredients with fallback chain.
        
        Returns:
            {
                "ingredients": "sugar, salt, flour",
                "model_used": "gemini" | "qwen" | "llava",
                "confidence": 0.95,
                "success": True
            }
        """
        prompt = self._build_prompt(language)
        
        # Try Gemini first
        result = await self._try_gemini(image_bytes, prompt)
        if result["success"]:
            return result
        
        # Try Qwen-VL
        result = await self._try_qwen(image_bytes, prompt)
        if result["success"]:
            return result
        
        # Try LLaVA
        result = await self._try_llava(image_bytes, prompt)
        if result["success"]:
            return result
        
        # All failed - return helpful error message
        print("❌ All vision models failed. Please check API keys.")
        return {
            "ingredients": None,
            "model_used": "none",
            "confidence": 0.0,
            "success": False,
            "error": "All vision models failed. Please check API keys and try again."
        }
    
    async def _try_gemini(self, image_bytes: bytes, prompt: str) -> Dict:
        """Try Gemini Pro Vision."""
        if not self.gemini_model:
            print("⚠️ Gemini model not initialized")
            return {"success": False}
        
        try:
            import PIL.Image
            import io
            
            # Convert bytes to PIL Image
            image = PIL.Image.open(io.BytesIO(image_bytes))
            
            # Generate content
            response = self.gemini_model.generate_content([prompt, image])
            
            # Check if response has text
            if not response or not hasattr(response, 'text'):
                print("❌ Gemini: No text in response")
                return {"success": False}
            
            # Some responses might be blocked for safety
            if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
                print(f"⚠️ Gemini blocked: {response.prompt_feedback}")
                return {"success": False}
            
            ingredients = self._clean_response(response.text)
            
            if not ingredients or len(ingredients) < 3:
                print("❌ Gemini: Empty or invalid response")
                return {"success": False}
            
            print(f"✅ Gemini extracted: {ingredients[:100]}...")
            
            return {
                "ingredients": ingredients,
                "model_used": "gemini-2.5-flash",
                "confidence": 0.95,
                "success": True
            }
        except Exception as e:
            print(f"❌ Gemini failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"success": False}
    
    async def _try_qwen(self, image_bytes: bytes, prompt: str) -> Dict:
        """Try Qwen-VL via HuggingFace Inference API."""
        if not self.hf_api_key:
            print("⚠️ No HuggingFace API key, skipping Qwen-VL")
            return {"success": False}
        
        try:
            import httpx
            
            # Encode image to base64
            image_b64 = base64.b64encode(image_bytes).decode()
            
            # HuggingFace Inference API
            api_url = "https://api-inference.huggingface.co/models/Qwen/Qwen-VL-Chat"
            headers = {"Authorization": f"Bearer {self.hf_api_key}"}
            
            payload = {
                "inputs": {
                    "image": image_b64,
                    "question": prompt
                }
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(api_url, headers=headers, json=payload)
                result = response.json()
                
                if isinstance(result, list) and len(result) > 0:
                    ingredients = self._clean_response(result[0].get("generated_text", ""))
                    print(f"✅ Qwen-VL extracted: {ingredients[:100]}...")
                    return {
                        "ingredients": ingredients,
                        "model_used": "qwen-vl",
                        "confidence": 0.85,
                        "success": True
                    }
            
            return {"success": False}
        except Exception as e:
            print(f"❌ Qwen-VL failed: {e}")
            return {"success": False}
    
    async def _try_llava(self, image_bytes: bytes, prompt: str) -> Dict:
        """Try LLaVA via HuggingFace Inference API."""
        if not self.hf_api_key:
            print("⚠️ No HuggingFace API key, skipping LLaVA")
            return {"success": False}
        
        try:
            import httpx
            
            image_b64 = base64.b64encode(image_bytes).decode()
            
            api_url = "https://api-inference.huggingface.co/models/llava-hf/llava-1.5-7b-hf"
            headers = {"Authorization": f"Bearer {self.hf_api_key}"}
            
            payload = {
                "inputs": {
                    "image": image_b64,
                    "text": prompt
                }
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(api_url, headers=headers, json=payload)
                result = response.json()
                
                if isinstance(result, list) and len(result) > 0:
                    ingredients = self._clean_response(result[0].get("generated_text", ""))
                    print(f"✅ LLaVA extracted: {ingredients[:100]}...")
                    return {
                        "ingredients": ingredients,
                        "model_used": "llava-1.5",
                        "confidence": 0.80,
                        "success": True
                    }
            
            return {"success": False}
        except Exception as e:
            print(f"❌ LLaVA failed: {e}")
            return {"success": False}
    
    async def _try_simple_ocr(self, image_bytes: bytes, language: str) -> Dict:
        """Fallback to simple OCR extraction."""
        try:
            import PIL.Image
            import io
            import pytesseract
            
            # Convert bytes to PIL Image
            image = PIL.Image.open(io.BytesIO(image_bytes))
            
            # Map language codes to Tesseract codes
            lang_map = {
                "hi": "hin", "bn": "ben", "ta": "tam", "te": "tel",
                "mr": "mar", "gu": "guj", "kn": "kan", "ml": "mal",
                "pa": "pan", "en": "eng"
            }
            tesseract_lang = lang_map.get(language, "eng")
            
            # Extract text
            text = pytesseract.image_to_string(image, lang=tesseract_lang)
            
            # Try to find ingredients section
            text_lower = text.lower()
            ingredients_text = ""
            
            # Look for ingredients keyword
            if "ingredients" in text_lower or "ingredient" in text_lower:
                lines = text.split('\n')
                capturing = False
                for line in lines:
                    if "ingredient" in line.lower():
                        capturing = True
                        # Get text after "ingredients:"
                        if ":" in line:
                            ingredients_text = line.split(":", 1)[1].strip()
                        continue
                    if capturing:
                        if line.strip() and not any(stop in line.lower() for stop in ["allergen", "nutrition", "storage", "best before"]):
                            ingredients_text += " " + line.strip()
                        elif line.strip() == "":
                            break
            
            ingredients_text = ingredients_text.strip()
            
            if ingredients_text and len(ingredients_text) > 10:
                print(f"✅ OCR fallback extracted: {ingredients_text[:100]}...")
                return {
                    "ingredients": ingredients_text,
                    "model_used": "tesseract-ocr",
                    "confidence": 0.60,
                    "success": True
                }
            
            print("❌ OCR: Could not find ingredients")
            return {"success": False}
        except Exception as e:
            print(f"❌ OCR fallback failed: {e}")
            return {"success": False}
    
    def _build_prompt(self, language: str) -> str:
        """Build vision prompt for ingredient extraction."""
        lang_instruction = ""
        if language != "en":
            langs = {
                "hi": "Hindi (हिन्दी)", "bn": "Bengali (বাংলা)", 
                "ta": "Tamil (தமிழ்)", "te": "Telugu (తెలుగు)",
                "mr": "Marathi (मराठी)", "gu": "Gujarati (ગુજરાતી)",
                "kn": "Kannada (ಕನ್ನಡ)", "ml": "Malayalam (മലയാളം)", 
                "pa": "Punjabi (ਪੰਜਾਬੀ)"
            }
            lang_instruction = f"\n\nIMPORTANT: Output ingredients in {langs.get(language, 'English')} language using native script."
        
        return f"""Look at this food product image and extract ONLY the ingredient list.

Instructions:
1. Find the "Ingredients:" or similar section on the package
2. Extract all ingredients in the order they appear
3. Return as a comma-separated list
4. Ignore nutrition facts, allergen warnings, barcodes, brand names
5. Fix any text errors or OCR-like mistakes
6. If ingredients are in multiple languages, prefer the clearest one{lang_instruction}

Return ONLY the ingredients as a comma-separated list, nothing else.
Format: ingredient1, ingredient2, ingredient3, ...

Ingredients:"""
    
    def _clean_response(self, text: str) -> str:
        """Clean and normalize model response."""
        text = text.strip()
        
        # Remove common prefixes
        prefixes = [
            "ingredients:", "answer:", "here are the ingredients:",
            "the ingredients are:", "ingredients list:"
        ]
        for prefix in prefixes:
            if text.lower().startswith(prefix):
                text = text[len(prefix):].strip()
        
        # Remove quotes
        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1]
        if text.startswith("'") and text.endswith("'"):
            text = text[1:-1]
        
        # Remove newlines
        text = text.replace("\n", " ").strip()
        
        return text


# Global instance
vision_extractor = VisionIngredientExtractor()
