"""
Direct test of the comprehensive analysis with detailed logging
"""

import requests
import json
import time

API_URL = "http://127.0.0.1:8000/api"

def test_with_many_ingredients():
    """Test with a realistic ingredient list"""
    
    # Realistic ingredient list with 10+ items
    ingredients = [
        "Refined Wheat Flour (Maida)",
        "Sugar",
        "Palm Oil",
        "Butter",
        "Eggs",
        "Cashew Nuts",
        "Salt",
        "Glucose Syrup",
        "Emulsifier (E471)",
        "Raising Agents (E503ii)",
        "Preservative (E223)",
        "Artificial Flavors",
        "Color (E102)"
    ]
    
    print("=" * 80)
    print("🧪 TESTING COMPREHENSIVE INGREDIENT ANALYSIS")
    print("=" * 80)
    print(f"\n📝 Testing with {len(ingredients)} ingredients:")
    for i, ing in enumerate(ingredients, 1):
        print(f"   {i}. {ing}")
    
    payload = {
        "ingredients": ingredients,
        "product_name": "Cookies",
        "language": "en",
        "include_eli5": False
    }
    
    print(f"\n🔄 Sending request to {API_URL}/analyze...")
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{API_URL}/analyze",
            json=payload,
            timeout=90
        )
        
        elapsed = time.time() - start_time
        print(f"✅ Response received in {elapsed:.1f}s")
        print(f"📊 Status Code: {response.status_code}\n")
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract detailed insights
            analysis_data = data.get("data", {})
            detailed_insights = analysis_data.get("detailed_insights", [])
            summary = analysis_data.get("summary", "")
            
            print(f"{'='*80}")
            print(f"📋 RESULTS:")
            print(f"{'='*80}\n")
            
            print(f"Summary: {summary[:200]}...\n")
            print(f"Total detailed insights: {len(detailed_insights)}")
            print(f"Expected: {len(ingredients)} ingredients\n")
            
            # Analyze each insight
            detailed_count = 0
            placeholder_count = 0
            
            print(f"{'='*80}")
            print(f"INGREDIENT ANALYSIS BREAKDOWN:")
            print(f"{'='*80}\n")
            
            for i, insight in enumerate(detailed_insights, 1):
                # Check if it's detailed or placeholder
                is_detailed = (
                    "Health Effects" in insight and
                    "Safety" in insight and
                    len(insight) > 200
                )
                
                is_placeholder = (
                    "Comprehensive analysis needed" in insight or
                    "analysis in progress" in insight or
                    "temporarily unavailable" in insight
                )
                
                if is_detailed:
                    detailed_count += 1
                    status = "✅ DETAILED"
                elif is_placeholder:
                    placeholder_count += 1
                    status = "⚠️ PLACEHOLDER"
                else:
                    status = "❓ PARTIAL"
                
                # Extract ingredient name
                lines = insight.split('\n')
                ing_name = lines[0].replace('###', '').strip() if lines else f"Ingredient {i}"
                
                print(f"{i:2}. {status:15} | {ing_name[:50]}")
            
            print(f"\n{'='*80}")
            print(f"📊 QUALITY METRICS:")
            print(f"{'='*80}")
            print(f"   Total insights:     {len(detailed_insights)}")
            print(f"   ✅ Detailed:        {detailed_count}")
            print(f"   ⚠️  Placeholders:    {placeholder_count}")
            print(f"   ❓ Partial:         {len(detailed_insights) - detailed_count - placeholder_count}")
            
            coverage = (detailed_count / len(ingredients) * 100) if len(ingredients) > 0 else 0
            print(f"   📈 Coverage:        {coverage:.1f}%")
            
            print(f"\n{'='*80}")
            
            if detailed_count >= len(ingredients) * 0.9:  # 90%+ coverage
                print("✅ EXCELLENT: Comprehensive analysis working!")
            elif detailed_count >= len(ingredients) * 0.7:  # 70%+ coverage
                print("⚠️ GOOD: Most ingredients analyzed, some missing")
            else:
                print("❌ NEEDS IMPROVEMENT: Many ingredients not analyzed")
                
            print(f"{'='*80}\n")
            
            # Show sample detailed insight
            if detailed_count > 0:
                print("📄 SAMPLE DETAILED ANALYSIS:")
                print("=" * 80)
                for insight in detailed_insights:
                    if "Health Effects" in insight and len(insight) > 200:
                        print(insight[:500] + "...\n")
                        break
            
            return detailed_count >= len(ingredients) * 0.7
            
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (>90s)")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🚀 Starting comprehensive ingredient analysis test...\n")
    
    # Wait a moment for server to be ready
    print("⏳ Waiting 2s for server...")
    time.sleep(2)
    
    success = test_with_many_ingredients()
    
    print("\n" + "=" * 80)
    if success:
        print("✅ TEST PASSED: Comprehensive analysis is working!")
    else:
        print("❌ TEST FAILED: Analysis needs improvement")
    print("=" * 80 + "\n")
