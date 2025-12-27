"""
Intent Inference Engine

Core innovation: Automatically infers user health intent from contextual clues
without requiring explicit user profiles or questionnaires.

PATENT HOOK: Context-aware intent detection for food decision-making.
"""

from typing import List, Dict, Optional
from enum import Enum


class UserIntent(Enum):
    """Detected user intents for food decisions."""
    GENERAL_HEALTH = "general_health"
    WEIGHT_MANAGEMENT = "weight_management"
    CHILD_SAFETY = "child_safety"
    ATHLETIC_PERFORMANCE = "athletic_performance"
    DISEASE_PREVENTION = "disease_prevention"
    QUICK_ENERGY = "quick_energy"
    LONG_TERM_HEALTH = "long_term_health"
    INGREDIENT_CONCERN = "ingredient_concern"


class FoodContext(Enum):
    """Types of food products."""
    PACKAGED_SNACK = "packaged_snack"
    BEVERAGE = "beverage"
    BREAKFAST_CEREAL = "breakfast_cereal"
    PROTEIN_SUPPLEMENT = "protein_supplement"
    BAKED_GOOD = "baked_good"
    PREPARED_MEAL = "prepared_meal"
    CONDIMENT = "condiment"
    CANDY = "candy"
    UNKNOWN = "unknown"


class IntentInferenceEngine:
    """
    Infers user intent based on:
    - Food type
    - Time of day (if available)
    - Ingredient patterns
    - Contextual clues
    """
    
    def __init__(self):
        self.intent_signals = {
            "sugar": [UserIntent.GENERAL_HEALTH, UserIntent.WEIGHT_MANAGEMENT],
            "protein": [UserIntent.ATHLETIC_PERFORMANCE, UserIntent.WEIGHT_MANAGEMENT],
            "artificial": [UserIntent.INGREDIENT_CONCERN, UserIntent.CHILD_SAFETY],
            "preservative": [UserIntent.LONG_TERM_HEALTH, UserIntent.INGREDIENT_CONCERN],
            "organic": [UserIntent.GENERAL_HEALTH, UserIntent.LONG_TERM_HEALTH],
        }
    
    def infer_food_context(self, ingredients: List[str], product_name: Optional[str] = None) -> FoodContext:
        """
        Determine what type of food product this is.
        """
        ingredients_lower = [ing.lower() for ing in ingredients]
        combined_text = " ".join(ingredients_lower)
        
        if product_name:
            combined_text += " " + product_name.lower()
        
        # Pattern matching for food types
        if any(word in combined_text for word in ["soda", "cola", "juice", "drink", "beverage"]):
            return FoodContext.BEVERAGE
        
        if any(word in combined_text for word in ["cereal", "oat", "granola", "corn flakes"]):
            return FoodContext.BREAKFAST_CEREAL
        
        if any(word in combined_text for word in ["whey", "protein", "bcaa", "creatine"]):
            return FoodContext.PROTEIN_SUPPLEMENT
        
        if any(word in combined_text for word in ["cookie", "cake", "brownie", "muffin", "pastry"]):
            return FoodContext.BAKED_GOOD
        
        if any(word in combined_text for word in ["candy", "chocolate", "gummy", "lollipop"]):
            return FoodContext.CANDY
        
        if any(word in combined_text for word in ["chips", "crackers", "popcorn", "pretzels", "snack"]):
            return FoodContext.PACKAGED_SNACK
        
        if any(word in combined_text for word in ["sauce", "ketchup", "mayo", "dressing", "mustard"]):
            return FoodContext.CONDIMENT
        
        if any(word in combined_text for word in ["frozen", "meal", "dinner", "lunch"]):
            return FoodContext.PREPARED_MEAL
        
        return FoodContext.UNKNOWN
    
    def infer_primary_intent(
        self,
        ingredients: List[str],
        food_context: FoodContext,
        user_question: Optional[str] = None
    ) -> UserIntent:
        """
        Infer what the user cares most about.
        
        This is the CORE INNOVATION - no explicit user input required.
        """
        ingredients_lower = [ing.lower() for ing in ingredients]
        
        # Check user question for explicit intent
        if user_question:
            question_lower = user_question.lower()
            
            if any(word in question_lower for word in ["kid", "child", "baby", "toddler"]):
                return UserIntent.CHILD_SAFETY
            
            if any(word in question_lower for word in ["lose weight", "diet", "calories"]):
                return UserIntent.WEIGHT_MANAGEMENT
            
            if any(word in question_lower for word in ["workout", "gym", "athletic", "muscle"]):
                return UserIntent.ATHLETIC_PERFORMANCE
            
            if any(word in question_lower for word in ["daily", "long term", "regularly"]):
                return UserIntent.LONG_TERM_HEALTH
        
        # Context-based inference
        if food_context == FoodContext.PROTEIN_SUPPLEMENT:
            return UserIntent.ATHLETIC_PERFORMANCE
        
        if food_context == FoodContext.CANDY:
            # Candy implies user is deciding on indulgence vs health
            return UserIntent.GENERAL_HEALTH
        
        if food_context == FoodContext.BREAKFAST_CEREAL:
            # Morning food implies daily consumption concern
            return UserIntent.LONG_TERM_HEALTH
        
        # Ingredient-based signals
        concerning_ingredients = [
            "artificial", "preservative", "color", "dye",
            "trans fat", "hydrogenated", "high fructose"
        ]
        
        has_concerning = any(
            any(concern in ing for concern in concerning_ingredients)
            for ing in ingredients_lower
        )
        
        if has_concerning:
            return UserIntent.INGREDIENT_CONCERN
        
        # High sugar products
        if any("sugar" in ing for ing in ingredients_lower):
            sugar_pos = next(i for i, ing in enumerate(ingredients_lower) if "sugar" in ing)
            if sugar_pos < 3:  # Sugar in top 3 ingredients
                return UserIntent.WEIGHT_MANAGEMENT
        
        # Default: general health awareness
        return UserIntent.GENERAL_HEALTH
    
    def generate_context_summary(
        self,
        food_context: FoodContext,
        primary_intent: UserIntent
    ) -> str:
        """
        Generate human-readable context summary.
        Used by reasoning engine to frame explanations.
        """
        context_descriptions = {
            FoodContext.PACKAGED_SNACK: "a packaged snack",
            FoodContext.BEVERAGE: "a beverage",
            FoodContext.BREAKFAST_CEREAL: "a breakfast cereal",
            FoodContext.PROTEIN_SUPPLEMENT: "a protein supplement",
            FoodContext.BAKED_GOOD: "a baked good",
            FoodContext.PREPARED_MEAL: "a prepared meal",
            FoodContext.CONDIMENT: "a condiment",
            FoodContext.CANDY: "a candy/sweet",
            FoodContext.UNKNOWN: "a food product"
        }
        
        intent_frames = {
            UserIntent.GENERAL_HEALTH: "health considerations",
            UserIntent.WEIGHT_MANAGEMENT: "weight and metabolism",
            UserIntent.CHILD_SAFETY: "child safety",
            UserIntent.ATHLETIC_PERFORMANCE: "athletic performance and recovery",
            UserIntent.DISEASE_PREVENTION: "long-term disease prevention",
            UserIntent.QUICK_ENERGY: "immediate energy needs",
            UserIntent.LONG_TERM_HEALTH: "long-term health impacts",
            UserIntent.INGREDIENT_CONCERN: "ingredient safety and transparency"
        }
        
        food_desc = context_descriptions.get(food_context, "a food product")
        intent_desc = intent_frames.get(primary_intent, "health")
        
        return f"This appears to be {food_desc}. Focusing on {intent_desc}."
    
    def analyze(
        self,
        ingredients: List[str],
        product_name: Optional[str] = None,
        user_question: Optional[str] = None
    ) -> Dict:
        """
        Complete intent analysis pipeline.
        
        Returns:
            {
                "food_context": FoodContext,
                "primary_intent": UserIntent,
                "context_summary": str,
                "confidence": float
            }
        """
        food_context = self.infer_food_context(ingredients, product_name)
        primary_intent = self.infer_primary_intent(ingredients, food_context, user_question)
        context_summary = self.generate_context_summary(food_context, primary_intent)
        
        # Confidence based on signal strength
        confidence = 0.8  # Default medium-high
        
        if user_question:
            confidence = 0.95  # Explicit intent from question
        elif food_context != FoodContext.UNKNOWN:
            confidence = 0.85
        
        return {
            "food_context": food_context.value,
            "primary_intent": primary_intent.value,
            "context_summary": context_summary,
            "confidence": confidence
        }


# Singleton instance
intent_engine = IntentInferenceEngine()
