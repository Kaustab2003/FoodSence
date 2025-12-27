"""
Debug test - check what the API actually returns
"""

import requests
import json

API_URL = "http://127.0.0.1:8000/api"

payload = {
    "ingredients": ["Butter", "Sugar", "Salt"],
    "product_name": "Test",
    "language": "en",
    "include_eli5": False
}

print("🔍 Sending test request...")

try:
    response = requests.post(
        f"{API_URL}/analyze",
        json=payload,
        timeout=60
    )
    
    print(f"Status: {response.status_code}\n")
    
    if response.status_code == 200:
        data = response.json()
        print("📦 Full Response Structure:")
        print(json.dumps(data, indent=2)[:2000])
        print("\n...")
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Error: {e}")
