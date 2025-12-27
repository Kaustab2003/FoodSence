"""
Live Demo Test - Verify ALL ingredients are analyzed
"""

import requests
import json

API_URL = "http://127.0.0.1:8000/api"

# Test with real-world example
test_cases = [
    {
        "name": "Cookies (Small List)",
        "ingredients": ["Butter", "Sugar", "Flour", "Eggs", "Salt"]
    },
    {
        "name": "Instant Noodles (Medium List)",
        "ingredients": [
            "Refined Wheat Flour",
            "Palm Oil",
            "Salt",
            "Sugar",
            "MSG (E621)",
            "Sodium Carbonate (E500)",
            "Potassium Carbonate (E501)",
            "Caramel Color (E150c)",
            "Citric Acid (E330)"
        ]
    },
    {
        "name": "Complex Snack (Large List)",
        "ingredients": [
            "Refined Wheat Flour (Maida)",
            "Sugar",
            "Palm Oil",
            "Butter",
            "Eggs",
            "Cashew Nuts (8%)",
            "Dry Fruits (Raisin, Cashew Nut)",
            "Salt",
            "Glucose Syrup",
            "Emulsifier (E471)",
            "Raising Agents (E503ii, E500ii)",
            "Preservative (E223)",
            "Artificial Flavors",
            "Color (E102)",
            "Antioxidant (E320)"
        ]
    }
]

def test_case(test_data):
    """Test a single case"""
    print(f"\n{'='*80}")
    print(f"🧪 TEST: {test_data['name']}")
    print(f"{'='*80}")
    
    ingredients = test_data['ingredients']
    print(f"📝 Input: {len(ingredients)} ingredients")
    for i, ing in enumerate(ingredients, 1):
        print(f"   {i}. {ing}")
    
    payload = {
        "ingredients": ingredients,
        "product_name": test_data['name'],
        "language": "en",
        "include_eli5": False
    }
    
    print(f"\n🔄 Analyzing...")
    
    try:
        response = requests.post(
            f"{API_URL}/analyze",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            detailed_insights = data.get("data", {}).get("detailed_insights", [])
            
            print(f"✅ Analysis complete!")
            print(f"\n📊 Output: {len(detailed_insights)} detailed analyses")
            
            # Verify all ingredients got analyzed
            if len(detailed_insights) >= len(ingredients):
                print(f"✅ SUCCESS: ALL {len(ingredients)} ingredients analyzed!")
            else:
                print(f"⚠️ WARNING: Only {len(detailed_insights)}/{len(ingredients)} analyzed")
            
            # Show ingredient names from analysis
            print(f"\n📋 Analyzed Ingredients:")
            for i, insight in enumerate(detailed_insights, 1):
                lines = insight.split('\n')
                name = lines[0].replace('###', '').strip() if lines else f"Item {i}"
                status = "✅" if "Health Effects" in insight else "⚠️"
                print(f"   {i}. {status} {name[:60]}")
            
            return len(detailed_insights) >= len(ingredients)
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text[:500])
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("\n🚀 COMPREHENSIVE INGREDIENT ANALYSIS - LIVE DEMO")
    print("="*80)
    print("This test verifies that ALL ingredients get detailed AI analysis")
    print("="*80)
    
    results = []
    for test in test_cases:
        success = test_case(test)
        results.append((test['name'], success))
    
    # Summary
    print(f"\n\n{'='*80}")
    print("📊 FINAL RESULTS")
    print(f"{'='*80}")
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status:10} - {name}")
    
    all_passed = all(r[1] for r in results)
    
    print(f"\n{'='*80}")
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("The system now analyzes EVERY ingredient comprehensively.")
        print("No matter how many ingredients you provide, ALL will be analyzed!")
    else:
        print("⚠️ Some tests failed - please review above")
    print(f"{'='*80}\n")
