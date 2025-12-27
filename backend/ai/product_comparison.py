"""
Product Comparison Feature

INNOVATION: Side-by-side AI-powered comparison of 2-3 products.
Highlights key differences for instant decision support.
"""

from typing import List, Dict
from pydantic import BaseModel
from ai.intent_inference import intent_engine
from ai.reasoning_engine import reasoning_engine


class ComparisonInsight(BaseModel):
    """Key difference between products."""
    category: str  # e.g., "Sugar Content", "Preservatives", "Nutritional Value"
    winner: int  # Product index (0, 1, or 2)
    explanation: str
    significance: str  # "high", "medium", "low"


class ComparisonResult(BaseModel):
    """Complete comparison result."""
    products: List[Dict]
    winner_index: int  # Overall best choice
    key_differences: List[ComparisonInsight]
    recommendation: str


def compare_products(products_data: List[Dict]) -> ComparisonResult:
    """
    Compare 2-3 products and determine the best choice.
    
    Args:
        products_data: List of dicts with 'ingredients' and 'name'
    
    Returns:
        ComparisonResult with winner and key differences
    """
    if len(products_data) < 2 or len(products_data) > 3:
        raise ValueError("Must compare 2-3 products")
    
    # Analyze each product
    analyses = []
    for product in products_data:
        intent_result = intent_engine.analyze(
            ingredients=product['ingredients'],
            product_name=product.get('name')
        )
        
        reasoning_result = reasoning_engine.analyze_ingredients(
            ingredients=product['ingredients'],
            intent=intent_result['primary_intent'],
            food_context=intent_result['food_context']
        )
        
        analyses.append({
            'product': product,
            'intent': intent_result,
            'reasoning': reasoning_result
        })
    
    # Determine winner (lowest risk, highest confidence)
    def score_product(analysis):
        signal_scores = {
            "likely_safe": 3,
            "moderate_concern": 2,
            "potential_risk": 1
        }
        confidence_scores = {
            "high": 3,
            "medium": 2,
            "low": 1
        }
        
        signal_score = signal_scores.get(analysis['reasoning'].overall_signal, 2)
        confidence_score = confidence_scores.get(analysis['reasoning'].overall_confidence, 2)
        
        return signal_score + confidence_score
    
    scores = [score_product(a) for a in analyses]
    winner_index = scores.index(max(scores))
    
    # Generate key differences
    key_differences = _extract_key_differences(analyses)
    
    # Generate recommendation
    recommendation = _generate_recommendation(analyses, winner_index)
    
    return ComparisonResult(
        products=[a['product'] for a in analyses],
        winner_index=winner_index,
        key_differences=key_differences,
        recommendation=recommendation
    )


def _extract_key_differences(analyses: List[Dict]) -> List[ComparisonInsight]:
    """
    Extract the most important differences between products.
    """
    differences = []
    
    # Compare health signals
    signals = [a['reasoning'].overall_signal for a in analyses]
    if len(set(signals)) > 1:
        best_idx = signals.index("likely_safe") if "likely_safe" in signals else 0
        differences.append(ComparisonInsight(
            category="Overall Safety",
            winner=best_idx,
            explanation=f"{analyses[best_idx]['product']['name']} has the safest overall ingredient profile",
            significance="high"
        ))
    
    # Compare number of concerns
    concern_counts = [
        len(a['reasoning'].insights[0].dict().get('concerns', []))
        for a in analyses
    ]
    min_concerns_idx = concern_counts.index(min(concern_counts))
    differences.append(ComparisonInsight(
        category="Ingredient Concerns",
        winner=min_concerns_idx,
        explanation=f"{analyses[min_concerns_idx]['product']['name']} has fewer concerning ingredients",
        significance="medium"
    ))
    
    # Compare research confidence
    confidences = [a['reasoning'].overall_confidence for a in analyses]
    if "high" in confidences:
        high_conf_idx = confidences.index("high")
        differences.append(ComparisonInsight(
            category="Research Quality",
            winner=high_conf_idx,
            explanation=f"{analyses[high_conf_idx]['product']['name']} has better-studied ingredients",
            significance="low"
        ))
    
    return differences[:3]  # Top 3 differences


def _generate_recommendation(analyses: List[Dict], winner_index: int) -> str:
    """
    Generate final recommendation text.
    """
    winner_name = analyses[winner_index]['product']['name']
    winner_signal = analyses[winner_index]['reasoning'].overall_signal
    
    if winner_signal == "likely_safe":
        return f"**Recommendation**: {winner_name} is your best choice with a safer ingredient profile and fewer health concerns."
    elif winner_signal == "moderate_concern":
        return f"**Recommendation**: {winner_name} is the better option among these, though consider consuming in moderation."
    else:
        return f"**Recommendation**: All options have concerns. {winner_name} is relatively better, but consider healthier alternatives if possible."
