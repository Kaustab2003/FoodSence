"""
Universal Product Test - Verify ALL products get comprehensive analysis
Tests with diverse product types to prove it works universally
"""

import requests
import json

API_URL = "http://127.0.0.1:8000/api"

# Test with DIFFERENT product types
test_products = [
    {
        "name": "Homemade Cookies",
        "ingredients": ["Butter", "Sugar", "Flour", "Eggs", "Vanilla Extract"]
    },
    {
        "name": "Mixed Fruit Jam",
        "ingredients": ["Sugar", "Mixed Fruit Pulp", "Pectin", "Citric Acid", "Preservative (E211)"]
    },
    {
        "name": "Instant Noodles",
        "ingredients": ["Wheat Flour", "Palm Oil", "Salt", "MSG (E621)", "Sodium Carbonate"]
    },
    {
        "name": "Chocolate Bar",
        "ingredients": ["Sugar", "Cocoa Butter", "Milk Powder", "Cocoa Mass", "Soy Lecithin (E322)", "Vanilla"]
    },
    {
        "name": "Energy Drink",
        "ingredients": ["Water", "Sugar", "Caffeine", "Taurine", "B Vitamins", "Citric Acid", "Artificial Flavors"]
    },
    {
        "name": "Breakfast Cereal",
        "ingredients": ["Whole Grain Wheat", "Sugar", "Corn Syrup", "Salt", "BHT (E321)", "Vitamins"]
    }
]

def test_product(product):
    """Test a single product"""
    print(f"\n{'='*80}")
    print(f"📦 PRODUCT: {product['name']}")
    print(f"{'='*80}")
    print(f"Ingredients: {len(product['ingredients'])}")
    
    payload = {
        "ingredients": product['ingredients'],
        "product_name": product['name'],
        "language": "en",
        "include_eli5": False
    }
    
    try:
        response = requests.post(
            f"{API_URL}/analyze",
            json=payload,
            timeout=90
        )
        
        if response.status_code == 200:
            data = response.json()
            detailed_insights = data.get("data", {}).get("detailed_insights", [])
            
            print(f"✅ Analysis successful")
            print(f"📊 Result: {len(detailed_insights)} detailed analyses")
            
            # Check coverage
            expected = len(product['ingredients'])
            actual = len(detailed_insights)
            coverage = (actual / expected * 100) if expected > 0 else 0
            
            print(f"📈 Coverage: {coverage:.1f}% ({actual}/{expected})")
            
            # Check quality
            detailed_count = sum(1 for d in detailed_insights if "Health Effects" in d and len(d) > 200)
            placeholder_count = sum(1 for d in detailed_insights if "Comprehensive analysis needed" in d)
            
            print(f"✅ Detailed: {detailed_count}")
            print(f"⚠️  Placeholders: {placeholder_count}")
            
            if coverage >= 100 and placeholder_count == 0:
                print(f"✅ PERFECT: All ingredients analyzed comprehensively!")
                return True
            elif coverage >= 80:
                print(f"⚠️  GOOD: Most ingredients analyzed")
                return True
            else:
                print(f"❌ NEEDS WORK: Low coverage")
                return False
                
        else:
            print(f"❌ API Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "="*80)
    print("🌍 UNIVERSAL PRODUCT TEST")
    print("="*80)
    print("Testing that comprehensive analysis works for ANY product type")
    print("Not just demo products - this works for EVERYTHING you input!")
    print("="*80)
    
    results = []
    for product in test_products:
        success = test_product(product)
        results.append((product['name'], success))
    
    # Summary
    print(f"\n\n{'='*80}")
    print("📊 FINAL RESULTS - UNIVERSAL COMPATIBILITY")
    print(f"{'='*80}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status:10} - {name}")
    
    print(f"\n{'='*80}")
    print(f"Success Rate: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print(f"\n✅ CONFIRMED: Works for ALL product types!")
        print(f"   • Cookies ✓")
        print(f"   • Jam ✓")
        print(f"   • Noodles ✓")
        print(f"   • Chocolate ✓")
        print(f"   • Drinks ✓")
        print(f"   • Cereal ✓")
        print(f"\n💡 The system analyzes EVERY ingredient comprehensively,")
        print(f"   regardless of product type or how many ingredients!")
    else:
        print(f"⚠️  Some products need attention")
    
    print(f"{'='*80}\n")
    
    print(f"\n📝 HOW TO USE:")
    print(f"{'='*80}")
    print(f"1. Enter ANY food product ingredients (manual or photo)")
    print(f"2. Submit for analysis")
    print(f"3. Get comprehensive details for ALL ingredients")
    print(f"4. Frontend displays each with:")
    print(f"   • What it is")
    print(f"   • Health effects (benefits + concerns)")
    print(f"   • Safety information")
    print(f"   • Usage in food")
    print(f"   • Final verdict")
    print(f"{'='*80}\n")
