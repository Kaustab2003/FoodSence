"""
Nutrition Facts Analysis Engine
Analyzes nutrition label data and provides health classification (Good/Moderate/Bad)
Based on WHO/FSSAI nutritional guidelines
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class NutritionData:
    """Structured nutrition facts data"""
    serving_size: Optional[str] = None
    servings_per_pack: Optional[float] = None
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbohydrates: Optional[float] = None
    total_sugars: Optional[float] = None
    added_sugars: Optional[float] = None
    total_fat: Optional[float] = None
    saturated_fat: Optional[float] = None
    mufa_fat: Optional[float] = None
    pufa_fat: Optional[float] = None
    trans_fat: Optional[float] = None
    cholesterol: Optional[float] = None
    sodium: Optional[float] = None
    dietary_fiber: Optional[float] = None
    
    # Additional metadata
    per_100g: bool = False  # If values are per 100g instead of per serving


class NutritionAnalyzer:
    """
    Analyzes nutrition facts and provides health classification
    """
    
    # WHO/FSSAI Guidelines (per serving)
    THRESHOLDS = {
        # Negatives
        "high_calories": 250,  # kcal per serving
        "high_added_sugar": 10,  # grams
        "high_total_sugar": 15,  # grams
        "high_saturated_fat": 5,  # grams
        "high_total_fat": 15,  # grams
        "high_sodium": 200,  # mg
        "any_trans_fat": 0.1,  # grams (any presence is bad)
        "high_cholesterol": 60,  # mg
        
        # Positives
        "good_protein": 5,  # grams (minimum)
        "good_fiber": 3,  # grams (minimum)
        "low_sodium": 100,  # mg (good level)
        "low_saturated_fat": 2,  # grams
    }
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze(self, nutrition_data: NutritionData) -> Dict:
        """
        Main analysis method - provides health classification
        
        Returns:
            {
                "classification": "Good" | "Moderate" | "Bad",
                "confidence": "High" | "Medium" | "Low",
                "key_positives": ["..."],
                "key_negatives": ["..."],
                "health_summary": "...",
                "recommended_consumption": "Regular" | "Occasional" | "Avoid",
                "nutrition_score": 0-100,
                "metrics": {...}
            }
        """
        try:
            # Calculate positive and negative scores
            positives = self._evaluate_positives(nutrition_data)
            negatives = self._evaluate_negatives(nutrition_data)
            
            # Determine confidence based on data completeness
            confidence = self._calculate_confidence(nutrition_data)
            
            # Calculate overall nutrition score (0-100)
            score = self._calculate_score(positives, negatives)
            
            # Classify as Good/Moderate/Bad
            classification = self._classify(score, negatives)
            
            # Generate recommendations
            recommendation = self._get_recommendation(classification, negatives)
            
            # Generate health summary
            summary = self._generate_summary(
                classification, 
                positives['items'], 
                negatives['items'],
                nutrition_data
            )
            
            return {
                "classification": classification,
                "confidence": confidence,
                "key_positives": positives['items'],
                "key_negatives": negatives['items'],
                "health_summary": summary,
                "recommended_consumption": recommendation,
                "nutrition_score": score,
                "metrics": {
                    "positive_score": positives['score'],
                    "negative_score": negatives['score'],
                    "critical_flags": negatives['critical_count']
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing nutrition data: {e}")
            return self._fallback_response()
    
    def _evaluate_positives(self, data: NutritionData) -> Dict:
        """Evaluate positive nutritional aspects"""
        items = []
        score = 0
        
        # High Protein (positive)
        if data.protein and data.protein >= self.THRESHOLDS["good_protein"]:
            items.append(f"Good protein content ({data.protein}g) - supports muscle health")
            score += 20
        
        # High Fiber (strong positive)
        if data.dietary_fiber and data.dietary_fiber >= self.THRESHOLDS["good_fiber"]:
            items.append(f"High dietary fiber ({data.dietary_fiber}g) - aids digestion")
            score += 25
        
        # Low Saturated Fat
        if data.saturated_fat and data.saturated_fat <= self.THRESHOLDS["low_saturated_fat"]:
            items.append(f"Low saturated fat ({data.saturated_fat}g) - heart-friendly")
            score += 15
        
        # Low Sodium
        if data.sodium and data.sodium <= self.THRESHOLDS["low_sodium"]:
            items.append(f"Low sodium ({data.sodium}mg) - good for blood pressure")
            score += 15
        
        # Healthy Fats (MUFA/PUFA)
        if data.mufa_fat and data.mufa_fat > 3:
            items.append(f"Contains healthy MUFA fats ({data.mufa_fat}g)")
            score += 10
        
        if data.pufa_fat and data.pufa_fat > 1:
            items.append(f"Contains omega fatty acids ({data.pufa_fat}g PUFA)")
            score += 10
        
        # Zero Trans Fat (positive)
        if data.trans_fat is not None and data.trans_fat == 0:
            items.append("Zero trans fat - no hydrogenated oils")
            score += 15
        
        return {"items": items, "score": score}
    
    def _evaluate_negatives(self, data: NutritionData) -> Dict:
        """Evaluate negative nutritional aspects"""
        items = []
        score = 0
        critical_count = 0
        
        # Trans Fat (CRITICAL - any amount is bad)
        if data.trans_fat and data.trans_fat > self.THRESHOLDS["any_trans_fat"]:
            items.append(f"⚠️ CRITICAL: Contains trans fat ({data.trans_fat}g) - increases heart disease risk")
            score += 40
            critical_count += 1
        
        # High Added Sugar (priority over total sugar)
        if data.added_sugars and data.added_sugars > self.THRESHOLDS["high_added_sugar"]:
            items.append(f"High added sugar ({data.added_sugars}g) - linked to obesity and diabetes")
            score += 25
        elif data.total_sugars and data.total_sugars > self.THRESHOLDS["high_total_sugar"]:
            items.append(f"High total sugar ({data.total_sugars}g) - monitor intake")
            score += 15
        
        # High Saturated Fat
        if data.saturated_fat and data.saturated_fat > self.THRESHOLDS["high_saturated_fat"]:
            items.append(f"High saturated fat ({data.saturated_fat}g) - raises LDL cholesterol")
            score += 20
        
        # High Sodium
        if data.sodium and data.sodium > self.THRESHOLDS["high_sodium"]:
            items.append(f"High sodium ({data.sodium}mg) - may increase blood pressure")
            score += 20
        
        # Excessive Calories
        if data.calories and data.calories > self.THRESHOLDS["high_calories"]:
            items.append(f"High calorie density ({data.calories} kcal) - portion control advised")
            score += 15
        
        # High Total Fat
        if data.total_fat and data.total_fat > self.THRESHOLDS["high_total_fat"]:
            items.append(f"High total fat ({data.total_fat}g) - calorie-dense")
            score += 10
        
        # High Cholesterol
        if data.cholesterol and data.cholesterol > self.THRESHOLDS["high_cholesterol"]:
            items.append(f"High cholesterol ({data.cholesterol}mg) - limit if you have heart issues")
            score += 10
        
        return {"items": items, "score": score, "critical_count": critical_count}
    
    def _calculate_score(self, positives: Dict, negatives: Dict) -> int:
        """Calculate overall nutrition score (0-100)"""
        # Start at 50 (neutral)
        base_score = 50
        
        # Add positives (max +50)
        positive_boost = min(positives['score'], 50)
        
        # Subtract negatives (max -50)
        negative_penalty = min(negatives['score'], 50)
        
        final_score = base_score + positive_boost - negative_penalty
        
        # Clamp between 0-100
        return max(0, min(100, final_score))
    
    def _classify(self, score: int, negatives: Dict) -> str:
        """Classify as Good/Moderate/Bad based on score and critical flags"""
        # Critical flags override score
        if negatives['critical_count'] > 0:
            return "Bad"
        
        # Score-based classification
        if score >= 70:
            return "Good"
        elif score >= 40:
            return "Moderate"
        else:
            return "Bad"
    
    def _get_recommendation(self, classification: str, negatives: Dict) -> str:
        """Get consumption recommendation"""
        if classification == "Good":
            return "Regular"
        elif classification == "Moderate":
            return "Occasional"
        else:
            # If critical issues, strongly avoid
            if negatives['critical_count'] > 0:
                return "Avoid"
            return "Occasional"
    
    def _calculate_confidence(self, data: NutritionData) -> str:
        """Calculate confidence based on data completeness"""
        # Count how many key fields are present
        key_fields = [
            data.calories,
            data.protein,
            data.total_fat,
            data.saturated_fat,
            data.carbohydrates,
            data.sodium
        ]
        
        present_count = sum(1 for field in key_fields if field is not None)
        
        if present_count >= 5:
            return "High"
        elif present_count >= 3:
            return "Medium"
        else:
            return "Low"
    
    def _generate_summary(self, classification: str, positives: List[str], 
                         negatives: List[str], data: NutritionData) -> str:
        """Generate consumer-friendly health summary"""
        if classification == "Good":
            summary = "This product has a favorable nutritional profile. "
        elif classification == "Moderate":
            summary = "This product has mixed nutritional qualities. "
        else:
            summary = "This product has concerning nutritional issues. "
        
        # Add key concerns/benefits
        if negatives:
            top_concern = negatives[0].replace("⚠️ CRITICAL: ", "").split(" - ")[0]
            summary += f"Main concern: {top_concern}. "
        
        if positives:
            top_benefit = positives[0].split(" - ")[0]
            summary += f"Notable benefit: {top_benefit}. "
        
        # Portion guidance
        if data.servings_per_pack and data.servings_per_pack > 1:
            summary += f"Package contains {data.servings_per_pack} servings - watch portion sizes."
        
        return summary
    
    def _fallback_response(self) -> Dict:
        """Fallback response when analysis fails"""
        return {
            "classification": "Unknown",
            "confidence": "Low",
            "key_positives": [],
            "key_negatives": ["Insufficient data to analyze"],
            "health_summary": "Unable to analyze nutrition facts. Please ensure image shows complete nutrition table.",
            "recommended_consumption": "Unknown",
            "nutrition_score": 0,
            "metrics": {
                "positive_score": 0,
                "negative_score": 0,
                "critical_flags": 0
            }
        }


def parse_nutrition_from_ocr(ocr_text: str) -> Optional[NutritionData]:
    """
    Parse structured nutrition data from OCR text
    This is a helper function to convert raw OCR text into NutritionData object
    
    Args:
        ocr_text: Raw text extracted from nutrition label
        
    Returns:
        NutritionData object or None if parsing fails
    """
    try:
        # This will be implemented with AI-powered parsing
        # For now, return None and let the vision model handle it
        return None
    except Exception as e:
        logger.error(f"Error parsing nutrition OCR: {e}")
        return None
