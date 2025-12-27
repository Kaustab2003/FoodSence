"""
Ingredient Deception Detector

PATENT INNOVATION: Deceptive ingredient detection and aggregation system
- Detects when same compound appears under multiple names
- Calculates cumulative impact of disguised ingredients
- Alerts users to "marketing tricks" in food labeling

Novel Approach:
- Multi-alias ingredient aggregation
- Surprise score calculation
- Consumer protection focus
"""

from typing import List, Dict, Optional
from pydantic import BaseModel


class DeceptionAlert(BaseModel):
    """Alert for deceptive ingredient practices."""
    alert_type: str  # 'hidden_sugar', 'sodium_overload', 'preservative_stack', etc.
    severity: str  # 'low', 'medium', 'high'
    surprise_score: int  # 0-100, higher = more deceptive
    title: str
    explanation: str
    disguised_ingredients: List[str]
    cumulative_impact: str


class DeceptionDetector:
    """
    Detects deceptive ingredient labeling practices.
    """
    
    def __init__(self):
        # Sugar aliases (most common deception)
        self.sugar_aliases = [
            'sugar', 'sucrose', 'glucose', 'fructose', 'dextrose', 'maltose',
            'lactose', 'galactose', 'corn syrup', 'high fructose corn syrup',
            'hfcs', 'corn sweetener', 'cane juice', 'evaporated cane juice',
            'cane sugar', 'beet sugar', 'brown sugar', 'raw sugar',
            'invert sugar', 'malt syrup', 'maple syrup', 'honey',
            'agave nectar', 'agave syrup', 'molasses', 'rice syrup',
            'brown rice syrup', 'barley malt', 'date sugar', 'coconut sugar',
            'fruit juice concentrate', 'maltodextrin'
        ]
        
        # Sodium aliases
        self.sodium_aliases = [
            'salt', 'sodium', 'sodium chloride', 'sea salt', 'himalayan salt',
            'sodium benzoate', 'sodium nitrate', 'sodium nitrite',
            'monosodium glutamate', 'msg', 'sodium bicarbonate',
            'baking soda', 'sodium phosphate', 'disodium phosphate',
            'trisodium phosphate', 'sodium citrate', 'sodium erythorbate'
        ]
        
        # Preservative families
        self.preservatives = [
            'sodium benzoate', 'potassium benzoate', 'calcium benzoate',
            'benzoic acid', 'bht', 'bha', 'tbhq', 'sulfites',
            'sodium sulfite', 'potassium sorbate', 'sorbic acid',
            'sodium nitrite', 'sodium nitrate', 'propyl gallate'
        ]
        
        # Artificial color families
        self.artificial_colors = [
            'red 40', 'red 3', 'yellow 5', 'yellow 6', 'blue 1', 'blue 2',
            'green 3', 'orange b', 'citrus red 2', 'allura red',
            'tartrazine', 'sunset yellow', 'brilliant blue'
        ]
        
        # Trans fat disguises
        self.trans_fat_indicators = [
            'partially hydrogenated', 'hydrogenated oil',
            'partially hydrogenated oil', 'shortening'
        ]
    
    def detect_deceptions(self, ingredients: List[str]) -> List[DeceptionAlert]:
        """
        Analyze ingredient list for deceptive practices.
        
        Returns list of deception alerts sorted by severity.
        """
        alerts = []
        
        # Normalize ingredient names
        normalized = [ing.lower().strip() for ing in ingredients]
        
        # Check for sugar stacking
        sugar_alert = self._detect_sugar_stacking(normalized)
        if sugar_alert:
            alerts.append(sugar_alert)
        
        # Check for sodium overload
        sodium_alert = self._detect_sodium_overload(normalized)
        if sodium_alert:
            alerts.append(sodium_alert)
        
        # Check for preservative cocktail
        preservative_alert = self._detect_preservative_cocktail(normalized)
        if preservative_alert:
            alerts.append(preservative_alert)
        
        # Check for artificial color rainbow
        color_alert = self._detect_color_cocktail(normalized)
        if color_alert:
            alerts.append(color_alert)
        
        # Check for trans fat hiding
        trans_fat_alert = self._detect_trans_fat_disguise(normalized)
        if trans_fat_alert:
            alerts.append(trans_fat_alert)
        
        # Sort by surprise score (highest first)
        alerts.sort(key=lambda x: x.surprise_score, reverse=True)
        
        return alerts
    
    def _detect_sugar_stacking(self, ingredients: List[str]) -> Optional[DeceptionAlert]:
        """
        Detect multiple sugar sources (most common deception).
        """
        found_sugars = []
        
        for ing in ingredients:
            for alias in self.sugar_aliases:
                if alias in ing:
                    found_sugars.append(ing)
                    break
        
        # Alert if 3+ sugar sources
        if len(found_sugars) >= 3:
            surprise_score = min(100, len(found_sugars) * 20 + 20)
            
            return DeceptionAlert(
                alert_type='hidden_sugar',
                severity='high' if len(found_sugars) >= 5 else 'medium',
                surprise_score=surprise_score,
                title=f"🚨 Sugar Stacking Detected ({len(found_sugars)} types)",
                explanation=f"This product contains {len(found_sugars)} different forms of sugar. "
                           f"Manufacturers often split sugar into multiple types to keep each one "
                           f"lower on the ingredient list, making the product appear healthier. "
                           f"Combined, these sugars likely make up a significant portion of the product.",
                disguised_ingredients=found_sugars,
                cumulative_impact=f"Total sugar content likely exceeds {len(found_sugars) * 3}g per serving"
            )
        
        return None
    
    def _detect_sodium_overload(self, ingredients: List[str]) -> Optional[DeceptionAlert]:
        """
        Detect multiple sodium sources.
        """
        found_sodium = []
        
        for ing in ingredients:
            for alias in self.sodium_aliases:
                if alias in ing:
                    found_sodium.append(ing)
                    break
        
        # Alert if 4+ sodium sources
        if len(found_sodium) >= 4:
            surprise_score = min(100, len(found_sodium) * 18)
            
            return DeceptionAlert(
                alert_type='sodium_overload',
                severity='high' if len(found_sodium) >= 6 else 'medium',
                surprise_score=surprise_score,
                title=f"⚠️ Sodium Overload ({len(found_sodium)} sources)",
                explanation=f"This product contains {len(found_sodium)} different sodium compounds. "
                           f"Each contributes to your daily sodium intake. High sodium consumption "
                           f"is linked to high blood pressure and cardiovascular issues.",
                disguised_ingredients=found_sodium,
                cumulative_impact=f"Likely exceeds 20% of daily sodium limit in one serving"
            )
        
        return None
    
    def _detect_preservative_cocktail(self, ingredients: List[str]) -> Optional[DeceptionAlert]:
        """
        Detect multiple preservatives (cocktail effect).
        """
        found_preservatives = []
        
        for ing in ingredients:
            for preservative in self.preservatives:
                if preservative in ing:
                    found_preservatives.append(ing)
                    break
        
        # Alert if 3+ preservatives
        if len(found_preservatives) >= 3:
            surprise_score = min(100, len(found_preservatives) * 22)
            
            return DeceptionAlert(
                alert_type='preservative_stack',
                severity='medium',
                surprise_score=surprise_score,
                title=f"🧪 Preservative Cocktail ({len(found_preservatives)} types)",
                explanation=f"This product uses {len(found_preservatives)} different preservatives. "
                           f"While each may be 'Generally Recognized as Safe' individually, "
                           f"the combined effect of multiple preservatives is less studied. "
                           f"Some people report sensitivities to preservative combinations.",
                disguised_ingredients=found_preservatives,
                cumulative_impact="Unknown long-term effects of combined preservatives"
            )
        
        return None
    
    def _detect_color_cocktail(self, ingredients: List[str]) -> Optional[DeceptionAlert]:
        """
        Detect multiple artificial colors.
        """
        found_colors = []
        
        for ing in ingredients:
            for color in self.artificial_colors:
                if color in ing:
                    found_colors.append(ing)
                    break
        
        # Alert if 3+ artificial colors
        if len(found_colors) >= 3:
            surprise_score = min(100, len(found_colors) * 25)
            
            return DeceptionAlert(
                alert_type='color_cocktail',
                severity='medium',
                surprise_score=surprise_score,
                title=f"🎨 Artificial Color Mix ({len(found_colors)} dyes)",
                explanation=f"This product contains {len(found_colors)} artificial food dyes. "
                           f"Some studies link certain combinations to hyperactivity in children. "
                           f"The EU requires warning labels on products with these color combinations.",
                disguised_ingredients=found_colors,
                cumulative_impact="May trigger behavioral changes in sensitive individuals, especially children"
            )
        
        return None
    
    def _detect_trans_fat_disguise(self, ingredients: List[str]) -> Optional[DeceptionAlert]:
        """
        Detect trans fat hiding (partially hydrogenated oils).
        """
        found_trans_fat = []
        
        for ing in ingredients:
            for indicator in self.trans_fat_indicators:
                if indicator in ing:
                    found_trans_fat.append(ing)
                    break
        
        if found_trans_fat:
            return DeceptionAlert(
                alert_type='trans_fat_hidden',
                severity='high',
                surprise_score=85,
                title="🚫 Hidden Trans Fats Detected",
                explanation="This product contains partially hydrogenated oils, which are a source of "
                           "trans fats. Even if the label says '0g trans fat', products can contain "
                           "up to 0.5g per serving and still claim zero. Trans fats are strongly "
                           "linked to heart disease and have been banned in many countries.",
                disguised_ingredients=found_trans_fat,
                cumulative_impact="Increases LDL (bad) cholesterol and decreases HDL (good) cholesterol"
            )
        
        return None
    
    def get_overall_deception_score(self, alerts: List[DeceptionAlert]) -> int:
        """
        Calculate overall "deception score" for product.
        
        Returns 0-100 (higher = more deceptive labeling)
        """
        if not alerts:
            return 0
        
        # Weight by severity
        total = 0
        for alert in alerts:
            if alert.severity == 'high':
                total += alert.surprise_score * 1.5
            elif alert.severity == 'medium':
                total += alert.surprise_score * 1.0
            else:
                total += alert.surprise_score * 0.5
        
        # Normalize to 0-100
        return min(100, int(total / len(alerts)))


# Singleton instance
deception_detector = DeceptionDetector()
