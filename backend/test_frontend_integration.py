"""
Frontend Integration Test
Tests that backend response includes detailed_insights and structure is correct
"""

import requests
import json

API_URL = "http://127.0.0.1:8000/api"

def test_frontend_integration():
    """Test the complete flow as frontend would use it"""
    
    print("=" * 80)
    print("🧪 FRONTEND INTEGRATION TEST")
    print("=" * 80)
    
    # Simulate frontend request with jam ingredients
    payload = {
        "ingredients": [
            "Sugar",
            "Mixed Fruit Pulp 45%",
            "Banana pulp",
            "Pineapple pulp",
            "Papaya pulp",
            "Mango pulp",
            "Alphonso mango pulp",
            "Guava pulp",
            "Apple juice",
            "Stabilizer (E440)",
            "Acidity Regulator (E330)",
            "Preservative (E211)"
        ],
        "product_name": "Mixed Fruit Jam",
        "language": "en",
        "include_eli5": False
    }
    
    print(f"\n📝 Testing with: {payload['product_name']}")
    print(f"   Ingredients: {len(payload['ingredients'])}")
    
    try:
        response = requests.post(
            f"{API_URL}/analyze",
            json=payload,
            timeout=90
        )
        
        print(f"\n✅ Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check structure
            print(f"\n📊 RESPONSE STRUCTURE CHECK:")
            print(f"   ✓ status: {data.get('status')}")
            print(f"   ✓ data object: {'present' if data.get('data') else 'MISSING'}")
            
            analysis_data = data.get('data', {})
            
            # Check key fields
            has_context = 'context' in analysis_data
            has_insights = 'insights' in analysis_data
            has_detailed_insights = 'detailed_insights' in analysis_data
            has_health_signal = 'health_signal' in analysis_data
            
            print(f"\n📋 REQUIRED FIELDS:")
            print(f"   {'✅' if has_context else '❌'} context")
            print(f"   {'✅' if has_insights else '❌'} insights (top priorities)")
            print(f"   {'✅' if has_detailed_insights else '❌'} detailed_insights (COMPREHENSIVE)")
            print(f"   {'✅' if has_health_signal else '❌'} health_signal")
            
            # Check detailed_insights content
            if has_detailed_insights:
                detailed = analysis_data['detailed_insights']
                print(f"\n🔍 DETAILED_INSIGHTS ANALYSIS:")
                print(f"   Type: {type(detailed)}")
                print(f"   Count: {len(detailed)}")
                print(f"   Expected: {len(payload['ingredients'])}")
                
                if len(detailed) > 0:
                    print(f"\n📄 SAMPLE INGREDIENT ANALYSIS:")
                    sample = detailed[0]
                    print(f"   Length: {len(sample)} characters")
                    print(f"   Format: {'Markdown' if '###' in sample else 'Unknown'}")
                    print(f"   Has sections: {all(x in sample for x in ['What it is', 'Health Effects', 'Safety', 'Final Verdict'])}")
                    print(f"\n   Preview:")
                    print("   " + "-" * 76)
                    for line in sample[:300].split('\n'):
                        print(f"   {line}")
                    print("   " + "-" * 76)
                
                # Check for placeholders (the problem we're fixing)
                placeholder_count = 0
                detailed_count = 0
                
                for insight in detailed:
                    if "Comprehensive analysis needed" in insight or "analysis in progress" in insight:
                        placeholder_count += 1
                    elif "Health Effects" in insight and len(insight) > 200:
                        detailed_count += 1
                
                print(f"\n📈 QUALITY METRICS:")
                print(f"   ✅ Detailed: {detailed_count}")
                print(f"   ⚠️  Placeholders: {placeholder_count}")
                print(f"   📊 Coverage: {detailed_count/len(detailed)*100:.1f}%")
                
                if placeholder_count > 0:
                    print(f"\n   ⚠️  WARNING: {placeholder_count} ingredients still showing placeholders!")
                    print(f"   This should NOT happen - all should have detailed analysis")
                else:
                    print(f"\n   ✅ PERFECT: All ingredients have detailed analysis!")
            
            # Check insights (old field)
            if has_insights:
                insights = analysis_data['insights']
                print(f"\n🎯 TOP PRIORITY INSIGHTS:")
                print(f"   Count: {len(insights)}")
                for i, insight in enumerate(insights, 1):
                    title = insight.get('title', 'No title')[:60]
                    print(f"   {i}. {title}")
            
            # Frontend usage guide
            print(f"\n" + "=" * 80)
            print(f"💡 FRONTEND USAGE:")
            print(f"=" * 80)
            print(f"To display in React/Next.js:")
            print(f"""
// Get data from API response
const analysisData = response.data.data

// Display comprehensive analysis for ALL ingredients
{{analysisData.detailed_insights?.map((detail, idx) => (
  <DetailedIngredientCard key={{idx}} content={{detail}} index={{idx}} />
))}}

// Display top priority summary
{{analysisData.insights.map((insight, idx) => (
  <InsightCard key={{idx}} insight={{insight}} />
))}}
            """)
            
            return detailed_count >= len(payload['ingredients']) * 0.9
            
        else:
            print(f"❌ API Error: {response.status_code}")
            print(response.text[:500])
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🚀 Testing Frontend Integration with Jam Ingredients...\n")
    
    success = test_frontend_integration()
    
    print("\n" + "=" * 80)
    if success:
        print("✅ TEST PASSED: Frontend integration ready!")
        print("All jam ingredients will show detailed analysis, not placeholders!")
    else:
        print("❌ TEST FAILED: Issues detected")
    print("=" * 80 + "\n")
