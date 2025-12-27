"""
Mock Ingredient Knowledge Base

This module contains curated ingredient data with health impacts,
research confidence levels, and contextual information.

Note: This is a simplified dataset for MVP demonstration.
Production version would integrate with comprehensive food databases.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel


class IngredientInfo(BaseModel):
    name: str
    category: str  # sweetener, preservative, additive, natural, etc.
    health_impact: str
    research_confidence: str  # high, medium, low
    concerns: List[str]
    benefits: List[str]
    safe_limit: Optional[str]
    common_in: List[str]


# Comprehensive ingredient knowledge base
INGREDIENT_DATABASE: Dict[str, IngredientInfo] = {
    # Sugars and Sweeteners
    "sugar": IngredientInfo(
        name="Sugar (Sucrose)",
        category="sweetener",
        health_impact="High consumption linked to energy spikes, crashes, and metabolic issues",
        research_confidence="high",
        concerns=[
            "Rapid blood sugar spikes followed by crashes",
            "May contribute to weight gain if consumed excessively",
            "Linked to dental cavities",
            "High intake associated with increased diabetes risk"
        ],
        benefits=[
            "Quick energy source",
            "Enhances taste and palatability",
            "Generally recognized as safe in moderation"
        ],
        safe_limit="Max 25g (women) / 37.5g (men) added sugar per day - WHO",
        common_in=["Sodas", "Candies", "Baked goods", "Processed snacks"]
    ),
    
    "high fructose corn syrup": IngredientInfo(
        name="High Fructose Corn Syrup (HFCS)",
        category="sweetener",
        health_impact="Similar to sugar but metabolized differently; linked to metabolic concerns",
        research_confidence="medium",
        concerns=[
            "May increase appetite more than regular sugar",
            "Linked to fatty liver disease in high amounts",
            "Potential metabolic syndrome association",
            "Bypasses normal satiety signals"
        ],
        benefits=[
            "Cost-effective sweetener",
            "Extends shelf life",
            "Blends well in liquids"
        ],
        safe_limit="Same as sugar - limit added sugars overall",
        common_in=["Soft drinks", "Fruit-flavored products", "Breakfast cereals"]
    ),

    "aspartame": IngredientInfo(
        name="Aspartame",
        category="artificial_sweetener",
        health_impact="Widely studied; safe for most but controversial",
        research_confidence="medium",
        concerns=[
            "Some people report headaches or sensitivity",
            "Not suitable for phenylketonuria (PKU) patients",
            "Long-term effects still debated",
            "May alter gut microbiome (emerging research)"
        ],
        benefits=[
            "Zero calories",
            "Does not raise blood sugar",
            "200x sweeter than sugar (less needed)"
        ],
        safe_limit="50mg/kg body weight per day - FDA",
        common_in=["Diet sodas", "Sugar-free gum", "Low-calorie desserts"]
    ),

    # Preservatives
    "sodium benzoate": IngredientInfo(
        name="Sodium Benzoate",
        category="preservative",
        health_impact="Generally safe but may form benzene in certain conditions",
        research_confidence="medium",
        concerns=[
            "Can form benzene (carcinogen) when combined with vitamin C and heat",
            "May trigger allergic reactions in sensitive individuals",
            "Possible link to hyperactivity in children (debated)",
            "Long-term effects under study"
        ],
        benefits=[
            "Prevents mold and yeast growth",
            "Extends shelf life significantly",
            "Low cost and widely approved"
        ],
        safe_limit="0-5 mg/kg body weight - WHO",
        common_in=["Soft drinks", "Pickles", "Sauces", "Fruit juices"]
    ),

    "potassium sorbate": IngredientInfo(
        name="Potassium Sorbate",
        category="preservative",
        health_impact="Generally recognized as safe with minimal concerns",
        research_confidence="high",
        concerns=[
            "Rare allergic reactions",
            "May cause mild skin irritation in sensitive people",
            "Effectiveness decreases in low-acid foods"
        ],
        benefits=[
            "Effective mold and yeast inhibitor",
            "Non-toxic at normal levels",
            "Does not affect taste significantly"
        ],
        safe_limit="25 mg/kg body weight - FDA",
        common_in=["Cheese", "Wine", "Dried fruits", "Baked goods"]
    ),

    "bht": IngredientInfo(
        name="BHT (Butylated Hydroxytoluene)",
        category="preservative",
        health_impact="Prevents oxidation but has mixed safety research",
        research_confidence="low",
        concerns=[
            "Potential endocrine disruptor",
            "May accumulate in body fat",
            "Animal studies show mixed results",
            "Banned in some countries"
        ],
        benefits=[
            "Prevents rancidity",
            "Extends shelf life of fatty foods",
            "Protects vitamins from degradation"
        ],
        safe_limit="0.3 mg/kg body weight - EU",
        common_in=["Cereals", "Chips", "Chewing gum", "Butter"]
    ),

    # Additives and Colorings
    "red 40": IngredientInfo(
        name="Red 40 (Allura Red)",
        category="food_coloring",
        health_impact="Widely used but linked to behavioral issues in some studies",
        research_confidence="low",
        concerns=[
            "May cause hyperactivity in sensitive children",
            "Possible allergic reactions",
            "Contains benzene precursors",
            "Long-term safety debated"
        ],
        benefits=[
            "Vibrant color enhancement",
            "Stable across pH ranges",
            "Cost-effective"
        ],
        safe_limit="7 mg/kg body weight - FDA",
        common_in=["Candies", "Soft drinks", "Desserts", "Sports drinks"]
    ),

    "yellow 5": IngredientInfo(
        name="Yellow 5 (Tartrazine)",
        category="food_coloring",
        health_impact="Common allergen; linked to behavioral changes",
        research_confidence="medium",
        concerns=[
            "Triggers asthma in aspirin-sensitive individuals",
            "May cause hives or itching",
            "Linked to hyperactivity (some studies)",
            "Requires labeling in EU"
        ],
        benefits=[
            "Bright yellow color",
            "Heat-stable",
            "Water-soluble"
        ],
        safe_limit="7.5 mg/kg body weight - FDA",
        common_in=["Chips", "Cereals", "Candy", "Soft drinks"]
    ),

    "monosodium glutamate": IngredientInfo(
        name="MSG (Monosodium Glutamate)",
        category="flavor_enhancer",
        health_impact="Safe for most but controversial; some report sensitivity",
        research_confidence="medium",
        concerns=[
            "Some people report headaches, sweating (MSG symptom complex)",
            "May increase appetite",
            "Sensitivity varies widely",
            "Stigma despite safety studies"
        ],
        benefits=[
            "Enhances umami (savory) flavor",
            "Reduces need for salt",
            "Naturally occurs in many foods"
        ],
        safe_limit="No specific limit - generally recognized as safe",
        common_in=["Chinese food", "Chips", "Soups", "Processed meats"]
    ),

    # Fats and Oils
    "partially hydrogenated oil": IngredientInfo(
        name="Partially Hydrogenated Oil",
        category="trans_fat",
        health_impact="Contains trans fats; strongly linked to heart disease",
        research_confidence="high",
        concerns=[
            "Raises LDL (bad) cholesterol",
            "Lowers HDL (good) cholesterol",
            "Increases heart disease risk",
            "Banned or restricted in many countries"
        ],
        benefits=[
            "Extends shelf life",
            "Solid at room temperature",
            "Cost-effective for manufacturers"
        ],
        safe_limit="Zero - WHO recommends elimination",
        common_in=["Margarine", "Fried foods", "Baked goods", "Microwave popcorn"]
    ),

    "palm oil": IngredientInfo(
        name="Palm Oil",
        category="saturated_fat",
        health_impact="High in saturated fat; environmental concerns",
        research_confidence="high",
        concerns=[
            "High saturated fat content",
            "May raise cholesterol",
            "Environmental deforestation impact",
            "Sustainability issues"
        ],
        benefits=[
            "Stable at high temperatures",
            "Semi-solid at room temperature",
            "Rich in vitamin E"
        ],
        safe_limit="Limit saturated fat to <10% of calories - AHA",
        common_in=["Cookies", "Ice cream", "Instant noodles", "Chocolate"]
    ),

    # Natural Ingredients
    "whole wheat flour": IngredientInfo(
        name="Whole Wheat Flour",
        category="natural_grain",
        health_impact="Nutritious whole grain with fiber and nutrients",
        research_confidence="high",
        concerns=[
            "Contains gluten (avoid if celiac/sensitive)",
            "Higher calorie density than vegetables",
            "May cause bloating in some people"
        ],
        benefits=[
            "High in dietary fiber",
            "Contains vitamins and minerals",
            "Supports digestive health",
            "Linked to lower heart disease risk"
        ],
        safe_limit="No limit - part of healthy diet",
        common_in=["Bread", "Pasta", "Cereals", "Crackers"]
    ),

    "oats": IngredientInfo(
        name="Oats",
        category="natural_grain",
        health_impact="Heart-healthy whole grain with beta-glucan fiber",
        research_confidence="high",
        concerns=[
            "May be contaminated with gluten during processing",
            "High in carbohydrates (manage portions)",
            "Instant varieties often have added sugar"
        ],
        benefits=[
            "Lowers cholesterol (beta-glucan)",
            "High in soluble fiber",
            "Stabilizes blood sugar",
            "Supports gut health"
        ],
        safe_limit="No limit - recommended daily",
        common_in=["Oatmeal", "Granola", "Cookies", "Energy bars"]
    ),

    "olive oil": IngredientInfo(
        name="Olive Oil",
        category="healthy_fat",
        health_impact="Heart-healthy monounsaturated fat with antioxidants",
        research_confidence="high",
        concerns=[
            "High in calories (use in moderation)",
            "Low smoke point for frying (extra virgin)",
            "Quality varies widely"
        ],
        benefits=[
            "Rich in monounsaturated fats",
            "Contains antioxidants",
            "Anti-inflammatory properties",
            "Linked to lower heart disease risk"
        ],
        safe_limit="2-3 tablespoons per day recommended",
        common_in=["Salad dressings", "Cooking", "Mediterranean dishes"]
    ),

    # Protein Sources
    "whey protein": IngredientInfo(
        name="Whey Protein",
        category="protein",
        health_impact="High-quality protein; generally safe for most people",
        research_confidence="high",
        concerns=[
            "May cause digestive issues (lactose)",
            "Possible acne in sensitive individuals",
            "Kidney stress if excessive (pre-existing conditions)",
            "Allergen for milk-sensitive people"
        ],
        benefits=[
            "Complete protein with all amino acids",
            "Supports muscle growth and recovery",
            "High bioavailability",
            "Satiating and filling"
        ],
        safe_limit="1-2 scoops (20-50g) per day typical",
        common_in=["Protein powders", "Bars", "Shakes", "Supplements"]
    ),

    "soy lecithin": IngredientInfo(
        name="Soy Lecithin",
        category="emulsifier",
        health_impact="Generally safe emulsifier from soybeans",
        research_confidence="high",
        concerns=[
            "Allergen for soy-sensitive individuals",
            "Often derived from GMO soybeans",
            "May contain trace pesticides",
            "Rare digestive upset"
        ],
        benefits=[
            "Improves texture and mixing",
            "Contains choline (brain health)",
            "Low dosage in foods",
            "Natural origin"
        ],
        safe_limit="No established limit - minimal amounts used",
        common_in=["Chocolate", "Baked goods", "Margarine", "Supplements"]
    ),

    # Sodium
    "salt": IngredientInfo(
        name="Salt (Sodium Chloride)",
        category="seasoning",
        health_impact="Essential mineral but excessive intake raises blood pressure",
        research_confidence="high",
        concerns=[
            "High intake increases blood pressure",
            "Linked to heart disease and stroke",
            "May worsen kidney disease",
            "Fluid retention and bloating"
        ],
        benefits=[
            "Essential electrolyte",
            "Preserves food",
            "Enhances flavor",
            "Nerve and muscle function"
        ],
        safe_limit="<2,300mg sodium per day (1 tsp salt) - FDA",
        common_in=["All processed foods", "Snacks", "Soups", "Deli meats"]
    ),

    # Protein Sources
    "whey protein": IngredientInfo(
        name="Whey Protein",
        category="protein",
        health_impact="High-quality protein source, well-studied for safety",
        research_confidence="high",
        concerns=[
            "May cause digestive issues in lactose-intolerant individuals",
            "Rare allergic reactions to milk proteins",
            "Kidney strain with excessive intake (pre-existing conditions)"
        ],
        benefits=[
            "Complete protein with all essential amino acids",
            "Supports muscle growth and recovery",
            "High in BCAAs (branched-chain amino acids)",
            "Easily digestible for most people"
        ],
        safe_limit="Up to 2g/kg body weight for active individuals",
        common_in=["Protein powders", "Protein bars", "Shakes", "Supplements"]
    ),

    # Grains
    "oats": IngredientInfo(
        name="Oats",
        category="whole_grain",
        health_impact="Whole grain with numerous health benefits",
        research_confidence="high",
        concerns=[
            "May contain gluten from cross-contamination",
            "High in carbs (not ideal for very low-carb diets)",
            "Phytic acid may reduce mineral absorption slightly"
        ],
        benefits=[
            "High in soluble fiber (beta-glucan)",
            "Helps lower cholesterol",
            "Stabilizes blood sugar",
            "Promotes digestive health"
        ],
        safe_limit="No upper limit - whole food",
        common_in=["Oatmeal", "Granola", "Protein bars", "Baked goods"]
    ),

    # Natural Sweeteners
    "honey": IngredientInfo(
        name="Honey",
        category="natural_sweetener",
        health_impact="Natural sugar with some antimicrobial properties",
        research_confidence="high",
        concerns=[
            "Still contains high amounts of sugar/calories",
            "Can spike blood sugar (though less than white sugar)",
            "Not suitable for infants under 1 year (botulism risk)",
            "Triggers dental cavities like regular sugar"
        ],
        benefits=[
            "Contains antioxidants and trace nutrients",
            "Natural antimicrobial properties",
            "May soothe sore throats",
            "Lower glycemic index than white sugar"
        ],
        safe_limit="Same as added sugars - moderation key",
        common_in=["Granola bars", "Tea", "Baked goods", "Cereals"]
    ),

    # Nuts
    "almonds": IngredientInfo(
        name="Almonds",
        category="nuts",
        health_impact="Nutrient-dense with heart-healthy fats",
        research_confidence="high",
        concerns=[
            "High in calories (easy to overconsume)",
            "Nut allergies can be severe",
            "Phytic acid reduces mineral absorption slightly",
            "Can cause digestive discomfort in sensitive individuals"
        ],
        benefits=[
            "Rich in vitamin E and magnesium",
            "Heart-healthy monounsaturated fats",
            "Good source of protein and fiber",
            "May help lower cholesterol"
        ],
        safe_limit="1 oz (23 almonds) = healthy serving",
        common_in=["Trail mix", "Protein bars", "Almond butter", "Baked goods"]
    ),

    # Chocolate
    "dark chocolate": IngredientInfo(
        name="Dark Chocolate",
        category="natural",
        health_impact="Contains antioxidants but also sugar and calories",
        research_confidence="medium",
        concerns=[
            "Contains caffeine (may affect sleep)",
            "High in calories and fat",
            "Often contains added sugar",
            "May trigger migraines in sensitive individuals"
        ],
        benefits=[
            "Rich in flavonoids (antioxidants)",
            "May improve heart health (70%+ cacao)",
            "Contains minerals like iron and magnesium",
            "May improve mood (theobromine)"
        ],
        safe_limit="1 oz dark chocolate (70%+ cacao) per day",
        common_in=["Protein bars", "Desserts", "Trail mix", "Baked goods"]
    ),

    "soy lecithin": IngredientInfo(
        name="Soy Lecithin",
        category="emulsifier",
        health_impact="Generally safe emulsifier derived from soybeans",
        research_confidence="high",
        concerns=[
            "May trigger soy allergies in sensitive individuals",
            "Often derived from GMO soybeans",
            "Rare digestive upset",
            "Potential estrogenic effects debated"
        ],
        benefits=[
            "Acts as natural emulsifier (blends ingredients)",
            "Contains choline (brain health)",
            "Prevents ingredient separation",
            "Low quantities used"
        ],
        safe_limit="No established limit - used in minimal amounts",
        common_in=["Chocolate", "Protein bars", "Margarine", "Baked goods"]
    ),
}


def get_ingredient_info(ingredient_name: str) -> Optional[IngredientInfo]:
    """
    Retrieve ingredient information from the database.
    Case-insensitive and handles variations.
    For unknown ingredients, creates a basic entry to ensure all ingredients are analyzed.
    """
    ingredient_lower = ingredient_name.lower().strip()
    
    # Direct match
    if ingredient_lower in INGREDIENT_DATABASE:
        return INGREDIENT_DATABASE[ingredient_lower]
    
    # Partial match (for variations)
    for key, info in INGREDIENT_DATABASE.items():
        if ingredient_lower in key or key in ingredient_lower:
            return info
    
    # Create placeholder for unknown ingredients (will be analyzed by AI later)
    return IngredientInfo(
        name=ingredient_name,
        category="unknown",
        health_impact=f"{ingredient_name} - detailed analysis will be provided",
        research_confidence="medium",
        concerns=["Comprehensive analysis needed"],
        benefits=["Analysis in progress"],
        safe_limit="Varies by usage",
        common_in=["Various food products"]
    )


def get_all_ingredients() -> List[str]:
    """Return list of all known ingredients."""
    return list(INGREDIENT_DATABASE.keys())


def get_ingredients_by_category(category: str) -> List[IngredientInfo]:
    """Get all ingredients in a specific category."""
    return [
        info for info in INGREDIENT_DATABASE.values()
        if info.category == category
    ]
