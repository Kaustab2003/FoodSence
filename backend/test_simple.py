"""
Quick test with fewer ingredients to see if AI is working
"""

import requests
import json

API_URL = "http://127.0.0.1:8000/api"

# Test with just 3 ingredients
payload = {
    "ingredients": ["Butter", "Sugar", "Salt"],
    "product_name": "Simple Test",
    "language": "en",
    "include_eli5": False
}

print("🧪 Testing with 3 simple ingredients: Butter, Sugar, Salt\n")
print("🔄 Sending request...")

try:
    response = requests.post(
        f"{API_URL}/analyze",
        json=payload,
        timeout=30
    )
    
    print(f"✅ Response Status: {response.status_code}\n")
    
    if response.status_code == 200:
        data = response.json()
        insights = data.get("data", {}).get("detailed_insights", [])
        
        print(f"📊 Got {len(insights)} insights:\n")
        
        for i, insight in enumerate(insights, 1):
            preview = insight[:200].replace('\n', ' ')
            print(f"{i}. {preview}...\n")
        
        # Check quality
        has_details = any("Health Effects" in ins or "Safety" in ins for ins in insights)
        
        if has_details:
            print("✅ AI analysis is working!")
        else:
            print("⚠️ Got responses but they may be placeholders")
            
    else:
        print(f"❌ Error: {response.text}")
        
except requests.exceptions.Timeout:
    print("❌ Timeout - backend may be processing")
except Exception as e:
    print(f"❌ Error: {e}")
