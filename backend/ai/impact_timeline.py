"""
Nutrition Impact Timeline

INNOVATION: Visualizes cumulative health effects of regular consumption.
Shows "what if I eat this daily for a week/month?"

Patent-worthy: Temporal health impact projection.
"""

from typing import List, Dict
from pydantic import BaseModel
from datetime import datetime, timedelta


class TimelineImpact(BaseModel):
    """Impact at a specific timeframe."""
    timeframe: str  # "1 day", "1 week", "1 month"
    cumulative_concerns: List[str]
    severity: str  # "low", "medium", "high"
    recommendation: str


class ImpactTimeline(BaseModel):
    """Complete timeline projection."""
    product_name: str
    frequency: str  # "daily", "weekly"
    timeline: List[TimelineImpact]
    overall_advice: str


def generate_impact_timeline(
    product_name: str,
    ingredients: List[str],
    health_concerns: List[str],
    frequency: str = "daily"
) -> ImpactTimeline:
    """
    Generate a timeline showing cumulative health impacts.
    
    Args:
        product_name: Name of the product
        ingredients: List of ingredients
        health_concerns: Identified health concerns from reasoning
        frequency: "daily" or "weekly"
    
    Returns:
        ImpactTimeline with projections
    """
    timeline_impacts = []
    
    # Day 1
    timeline_impacts.append(TimelineImpact(
        timeframe="1 Day",
        cumulative_concerns=health_concerns[:1] if health_concerns else ["Minimal immediate impact"],
        severity="low",
        recommendation="Single consumption is generally manageable"
    ))
    
    # Week 1
    weekly_concerns = _extrapolate_concerns(health_concerns, days=7)
    timeline_impacts.append(TimelineImpact(
        timeframe="1 Week",
        cumulative_concerns=weekly_concerns,
        severity=_calculate_severity(len(weekly_concerns)),
        recommendation=_generate_weekly_recommendation(len(weekly_concerns))
    ))
    
    # Month 1
    monthly_concerns = _extrapolate_concerns(health_concerns, days=30)
    timeline_impacts.append(TimelineImpact(
        timeframe="1 Month",
        cumulative_concerns=monthly_concerns,
        severity=_calculate_severity(len(monthly_concerns)),
        recommendation=_generate_monthly_recommendation(len(monthly_concerns))
    ))
    
    # Overall advice
    overall_advice = _generate_overall_advice(health_concerns, frequency)
    
    return ImpactTimeline(
        product_name=product_name,
        frequency=frequency,
        timeline=timeline_impacts,
        overall_advice=overall_advice
    )


def _extrapolate_concerns(base_concerns: List[str], days: int) -> List[str]:
    """
    Project cumulative concerns over time.
    """
    if not base_concerns:
        return ["No significant concerns identified"]
    
    extrapolated = []
    
    for concern in base_concerns:
        if "sugar" in concern.lower():
            if days >= 7:
                extrapolated.append(f"Regular sugar intake may affect energy stability and weight")
            if days >= 30:
                extrapolated.append(f"Monthly sugar accumulation increases metabolic stress")
        
        if "preservative" in concern.lower() or "artificial" in concern.lower():
            if days >= 7:
                extrapolated.append(f"Weekly additive exposure - body adapts but may accumulate")
            if days >= 30:
                extrapolated.append(f"Long-term additive consumption effects still debated")
        
        if "fat" in concern.lower() or "oil" in concern.lower():
            if days >= 7:
                extrapolated.append(f"Regular saturated fat may impact cholesterol levels")
            if days >= 30:
                extrapolated.append(f"Monthly fat intake patterns affect cardiovascular health")
    
    return extrapolated if extrapolated else base_concerns


def _calculate_severity(concern_count: int) -> str:
    """Determine severity based on number of concerns."""
    if concern_count <= 1:
        return "low"
    elif concern_count <= 3:
        return "medium"
    else:
        return "high"


def _generate_weekly_recommendation(concern_count: int) -> str:
    """Generate recommendation for weekly consumption."""
    if concern_count <= 1:
        return "Weekly consumption appears manageable - enjoy in moderation"
    elif concern_count <= 3:
        return "Consider limiting to 2-3 times per week maximum"
    else:
        return "Recommend finding healthier alternatives for regular consumption"


def _generate_monthly_recommendation(concern_count: int) -> str:
    """Generate recommendation for monthly patterns."""
    if concern_count <= 1:
        return "Monthly patterns suggest minimal long-term risk with moderation"
    elif concern_count <= 3:
        return "Consider varying your diet to reduce cumulative effects"
    else:
        return "Long-term daily consumption not recommended - explore alternatives"


def _generate_overall_advice(concerns: List[str], frequency: str) -> str:
    """Generate personalized overall advice."""
    if not concerns or len(concerns) == 0:
        return f"This product appears safe for {frequency} consumption based on current research."
    
    if frequency == "daily":
        if len(concerns) > 2:
            return "⚠️ Daily consumption may lead to cumulative health effects. Consider as an occasional treat instead."
        else:
            return "⚖️ Daily use is possible, but moderation and variety in your diet is key."
    
    else:  # weekly
        if len(concerns) > 2:
            return "⚖️ Weekly consumption is more reasonable, but monitor overall dietary patterns."
        else:
            return "✅ Weekly consumption appears manageable within a balanced diet."
