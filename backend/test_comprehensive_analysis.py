"""
Test script for comprehensive ingredient analysis
Tests the full pipeline with parsing, AI analysis, and error handling
"""

import requests
import json

API_URL = "http://127.0.0.1:8000/api"

def test_comprehensive_analysis():
    """Test comprehensive ingredient analysis with complex ingredient list"""
    
    # Test data: Complex ingredient list with parentheses
    test_ingredients = "Butter, Eggs, Refined Wheat Flour (Maida), Sugar, Palm Oil, Cashew Nuts (8%), Dry Fruits (Raisin, Cashew Nut), Glucose Syrup, Salt, Emulsifier (E471), Raising Agents (E503ii, E500ii), Artificial Flavors, Preservative (E223), Color (E102)"
    
    print("=" * 80)
    print("🧪 COMPREHENSIVE ANALYSIS TEST")
    print("=" * 80)
    print(f"\n📝 Testing with ingredient string:")
    print(f"   {test_ingredients[:100]}...\n")
    
    # Make API request
    payload = {
        "ingredients": [test_ingredients],  # Send as single string to trigger parsing
        "product_name": "Test Cookies",
        "language": "en",
        "include_eli5": False
    }
    
    print("🔄 Sending request to /api/analyze...")
    
    try:
        response = requests.post(
            f"{API_URL}/analyze",
            json=payload,
            timeout=60
        )
        
        print(f"✅ Response Status: {response.status_code}\n")
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract results
            analysis_data = data.get("data", {})
            detailed_insights = analysis_data.get("detailed_insights", [])
            
            print(f"📊 RESULTS:")
            print(f"   Total insights: {len(detailed_insights)}")
            print(f"\n{'='*80}\n")
            
            # Check each insight
            placeholder_count = 0
            real_analysis_count = 0
            
            for i, insight in enumerate(detailed_insights, 1):
                # Check if it's a placeholder
                is_placeholder = (
                    "Comprehensive analysis needed" in insight or
                    "analysis in progress" in insight or
                    "temporarily unavailable" in insight or
                    len(insight) < 100
                )
                
                if is_placeholder:
                    placeholder_count += 1
                    status = "⚠️ PLACEHOLDER"
                else:
                    real_analysis_count += 1
                    status = "✅ DETAILED"
                
                # Print preview
                preview = insight[:150].replace('\n', ' ')
                print(f"{i}. {status}: {preview}...")
            
            print(f"\n{'='*80}\n")
            print(f"📈 ANALYSIS QUALITY:")
            print(f"   ✅ Detailed Analysis: {real_analysis_count}")
            print(f"   ⚠️ Placeholders: {placeholder_count}")
            print(f"   📊 Success Rate: {real_analysis_count/(real_analysis_count+placeholder_count)*100:.1f}%\n")
            
            if real_analysis_count < len(detailed_insights) * 0.7:
                print("❌ TEST FAILED: Less than 70% of ingredients have detailed analysis")
                print("\n🔍 DEBUGGING TIPS:")
                print("   1. Check backend logs for AI errors")
                print("   2. Verify Gemini API key is valid")
                print("   3. Check API quota limits")
                print("   4. Review ingredient parsing output")
                return False
            else:
                print("✅ TEST PASSED: Comprehensive analysis working!")
                return True
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (>60s)")
        print("   This may indicate AI processing is taking too long")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_parsing_only():
    """Test just the ingredient parsing"""
    print("\n" + "=" * 80)
    print("🧪 PARSING TEST")
    print("=" * 80 + "\n")
    
    from utils.ingredient_parser import smart_ingredient_split
    
    test_string = "Butter, Eggs, Dry Fruits (Raisin, Cashew Nut), Sugar"
    result = smart_ingredient_split(test_string)
    
    print(f"Input:  {test_string}")
    print(f"Output: {result}")
    print(f"Count:  {len(result)} ingredients\n")
    
    expected = ['Butter', 'Eggs', 'Dry Fruits (Raisin, Cashew Nut)', 'Sugar']
    if result == expected:
        print("✅ Parsing test passed!")
        return True
    else:
        print(f"❌ Parsing test failed!")
        print(f"   Expected: {expected}")
        print(f"   Got: {result}")
        return False


if __name__ == "__main__":
    print("\n🚀 Starting comprehensive test suite...\n")
    
    # Test 1: Parsing
    parsing_ok = test_parsing_only()
    
    # Test 2: Full analysis
    analysis_ok = test_comprehensive_analysis()
    
    print("\n" + "=" * 80)
    print("📋 TEST SUMMARY")
    print("=" * 80)
    print(f"   Parsing: {'✅ PASS' if parsing_ok else '❌ FAIL'}")
    print(f"   Comprehensive Analysis: {'✅ PASS' if analysis_ok else '❌ FAIL'}")
    print("=" * 80 + "\n")
