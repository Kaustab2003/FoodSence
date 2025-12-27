"""
Reasoning Engine

Converts ingredient lists into 3 human-level insights with confidence scoring.
This is the core logic that reduces cognitive load.

INNOVATION: Intelligent compression of complex data into actionable insights.
"""

from typing import List, Dict, Optional
from pydantic import BaseModel
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.mock_ingredient_data import get_ingredient_info, IngredientInfo
from ai.intent_inference import UserIntent, FoodContext


class HealthSignal(str):
    """Health signal categories."""
    LIKELY_SAFE = "likely_safe"
    MODERATE_CONCERN = "moderate_concern"
    POTENTIAL_RISK = "potential_risk"


class Insight(BaseModel):
    """A single insight about the food product."""
    title: str
    explanation: str
    concern_level: str  # positive, neutral, negative
    confidence: str  # high, medium, low
    icon: str  # emoji for visual communication


class ReasoningResult(BaseModel):
    """Complete reasoning output."""
    overall_signal: str  # HealthSignal
    overall_confidence: str
    insights: List[Insight]
    trade_offs: Dict[str, List[str]]  # {"benefits": [...], "downsides": [...]}
    uncertainty_note: Optional[str]


class ReasoningEngine:
    """
    Analyzes ingredients and generates human-level insights.
    """
    
    def __init__(self):
        self.max_insights = 100  # Analyze ALL ingredients for comprehensive report
    
    def analyze_ingredients(
        self,
        ingredients: List[str],
        intent: UserIntent,
        food_context: FoodContext
    ) -> ReasoningResult:
        """
        Main analysis pipeline.
        
        Steps:
        1. Match ingredients to knowledge base
        2. Prioritize by relevance to intent
        3. Generate top 3 insights
        4. Determine overall health signal
        5. Extract trade-offs
        6. Add uncertainty notes
        """
        # Step 1: Match ingredients
        matched_ingredients = self._match_ingredients(ingredients)
        
        # Step 2: Prioritize by intent and research confidence
        prioritized = self._prioritize_ingredients(
            matched_ingredients,
            intent,
            food_context
        )
        
        # Step 3: Generate insights (top 3)
        insights = self._generate_insights(prioritized[:self.max_insights], intent)
        
        # Step 4: Overall health signal
        overall_signal, signal_confidence = self._determine_health_signal(prioritized)
        
        # Step 5: Trade-offs
        trade_offs = self._extract_trade_offs(prioritized)
        
        # Step 6: Uncertainty
        uncertainty_note = self._generate_uncertainty_note(prioritized)
        
        return ReasoningResult(
            overall_signal=overall_signal,
            overall_confidence=signal_confidence,
            insights=insights,
            trade_offs=trade_offs,
            uncertainty_note=uncertainty_note
        )
    
    def _match_ingredients(self, ingredients: List[str]) -> List[IngredientInfo]:
        """Match ingredient names to knowledge base."""
        matched = []
        
        for ingredient in ingredients:
            info = get_ingredient_info(ingredient)
            if info:
                matched.append(info)
        
        return matched
    
    def _prioritize_ingredients(
        self,
        ingredients: List[IngredientInfo],
        intent: UserIntent,
        food_context: FoodContext
    ) -> List[IngredientInfo]:
        """
        Sort ingredients by relevance to user intent.
        
        Priority factors:
        - Research confidence
        - Severity of concerns
        - Relevance to intent
        - Position in ingredient list (first = most abundant)
        """
        def priority_score(ing: IngredientInfo) -> float:
            score = 0.0
            
            # Higher concern = higher priority
            if len(ing.concerns) > 3:
                score += 3.0
            elif len(ing.concerns) > 1:
                score += 2.0
            elif len(ing.concerns) > 0:
                score += 1.0
            
            # Research confidence
            confidence_scores = {"high": 3.0, "medium": 2.0, "low": 1.5}
            score += confidence_scores.get(ing.research_confidence, 1.0)
            
            # Intent-specific boosting
            if intent == UserIntent.WEIGHT_MANAGEMENT:
                if ing.category in ["sweetener", "saturated_fat", "trans_fat"]:
                    score += 2.0
            
            elif intent == UserIntent.CHILD_SAFETY:
                if ing.category in ["artificial_sweetener", "food_coloring", "preservative"]:
                    score += 2.0
            
            elif intent == UserIntent.ATHLETIC_PERFORMANCE:
                if ing.category in ["protein", "natural_grain"]:
                    score += 2.0
            
            elif intent == UserIntent.INGREDIENT_CONCERN:
                if "artificial" in ing.category or "preservative" in ing.category:
                    score += 2.0
            
            return score
        
        return sorted(ingredients, key=priority_score, reverse=True)
    
    def _generate_insights(
        self,
        ingredients: List[IngredientInfo],
        intent: UserIntent
    ) -> List[Insight]:
        """
        Generate insights for ALL matched ingredients.
        """
        insights = []
        
        for ing in ingredients:  # Analyze ALL ingredients
            # Determine concern level
            concern_level = "neutral"
            icon = "ℹ️"
            
            if len(ing.concerns) > 2:
                concern_level = "negative"
                icon = "⚠️"
            elif len(ing.concerns) > 0:
                concern_level = "neutral"
                icon = "🔍"
            elif len(ing.benefits) > len(ing.concerns):
                concern_level = "positive"
                icon = "✅"
            
            # Generate human-friendly title
            if concern_level == "negative":
                title = f"{ing.name} – Potential Concern"
            elif concern_level == "positive":
                title = f"{ing.name} – Beneficial"
            else:
                title = f"{ing.name} – Mixed Evidence"
            
            # Build explanation (1-2 sentences)
            explanation = ing.health_impact
            
            # Add most relevant concern/benefit
            if ing.concerns and concern_level != "positive":
                explanation += f" {ing.concerns[0]}."
            elif ing.benefits:
                explanation += f" {ing.benefits[0]}."
            
            insights.append(Insight(
                title=title,
                explanation=explanation,
                concern_level=concern_level,
                confidence=ing.research_confidence,
                icon=icon
            ))
        
        # No need to fill with generic insights - we have all real ingredients
        if len(insights) == 0:
            insights.append(Insight(
                title="Limited Information",
                explanation="Some ingredients in this product are not in our database yet.",
                concern_level="neutral",
                confidence="low",
                icon="🔍"
            ))
        
        return insights
    
    def _determine_health_signal(
        self,
        ingredients: List[IngredientInfo]
    ) -> tuple[str, str]:
        """
        Determine overall health signal: 🟢🟡🔴
        
        Returns: (signal, confidence)
        """
        if not ingredients:
            return (HealthSignal.MODERATE_CONCERN, "low")
        
        # Count concerning ingredients
        high_concern_count = sum(
            1 for ing in ingredients
            if len(ing.concerns) > 2 or ing.category in ["trans_fat", "artificial_sweetener"]
        )
        
        medium_concern_count = sum(
            1 for ing in ingredients
            if len(ing.concerns) > 0 and len(ing.concerns) <= 2
        )
        
        low_confidence_count = sum(
            1 for ing in ingredients
            if ing.research_confidence == "low"
        )
        
        total = len(ingredients)
        
        # Decision logic
        if high_concern_count >= 2 or (high_concern_count == 1 and total <= 3):
            signal = HealthSignal.POTENTIAL_RISK
            confidence = "high" if low_confidence_count == 0 else "medium"
        
        elif medium_concern_count >= total / 2:
            signal = HealthSignal.MODERATE_CONCERN
            confidence = "medium"
        
        else:
            signal = HealthSignal.LIKELY_SAFE
            confidence = "high" if low_confidence_count == 0 else "medium"
        
        return (signal, confidence)
    
    def _extract_trade_offs(
        self,
        ingredients: List[IngredientInfo]
    ) -> Dict[str, List[str]]:
        """
        Extract benefits vs downsides.
        Returns up to 3 of each.
        """
        all_benefits = []
        all_downsides = []
        
        for ing in ingredients:
            all_benefits.extend(ing.benefits)
            all_downsides.extend(ing.concerns)
        
        # Deduplicate and limit
        unique_benefits = list(set(all_benefits))[:3]
        unique_downsides = list(set(all_downsides))[:3]
        
        return {
            "benefits": unique_benefits,
            "downsides": unique_downsides
        }
    
    def _generate_uncertainty_note(
        self,
        ingredients: List[IngredientInfo]
    ) -> Optional[str]:
        """
        Generate honest uncertainty communication.
        """
        low_confidence = [
            ing for ing in ingredients
            if ing.research_confidence == "low"
        ]
        
        if not low_confidence:
            return None
        
        if len(low_confidence) == 1:
            return f"Research on {low_confidence[0].name} is still evolving. Long-term effects are not fully understood."
        
        elif len(low_confidence) > 1:
            return f"Several ingredients ({', '.join([i.name for i in low_confidence[:2]])}) have limited long-term research. Effects may vary individually."
        
        return "Some ingredients lack comprehensive long-term studies. Consider moderation."


# Singleton instance
reasoning_engine = ReasoningEngine()
