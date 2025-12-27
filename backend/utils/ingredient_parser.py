"""
Smart Ingredient Parser

Handles complex ingredient strings with parentheses, commas, and nested structures.
Example: "Dry Fruits (Raisin, Cashew Nut)" stays as one ingredient.
"""

from typing import List, Union


def smart_ingredient_split(ingredients_input: Union[str, List[str]]) -> List[str]:
    """
    Split ingredients intelligently, respecting parentheses.
    
    Args:
        ingredients_input: String with comma-separated ingredients or list of ingredients
        
    Returns:
        List of individual ingredients
        
    Examples:
        >>> smart_ingredient_split("Butter, Eggs, Dry Fruits (Raisin, Cashew Nut)")
        ['Butter', 'Eggs', 'Dry Fruits (Raisin, Cashew Nut)']
        
        >>> smart_ingredient_split("Sugar, Salt, Flour")
        ['Sugar', 'Salt', 'Flour']
    """
    # If already a list, return as is
    if isinstance(ingredients_input, list):
        return ingredients_input
    
    result = []
    current = ""
    paren_depth = 0
    
    for char in ingredients_input:
        if char == '(':
            paren_depth += 1
            current += char
        elif char == ')':
            paren_depth -= 1
            current += char
        elif char == ',' and paren_depth == 0:
            # Only split on commas outside parentheses
            if current.strip():
                result.append(current.strip())
            current = ""
        else:
            current += char
    
    # Add last ingredient
    if current.strip():
        result.append(current.strip())
    
    return result


if __name__ == "__main__":
    # Test cases
    test_cases = [
        "Butter, Eggs, Dry Fruits (Raisin, Cashew Nut)",
        "Sugar, Salt, Flour",
        "Palm Oil, Cashew Nuts (8%), Glucose Syrup",
        "Refined Wheat Flour (Maida), Sugar, Eggs"
    ]
    
    print("🧪 Testing smart ingredient parsing:\n")
    for test in test_cases:
        result = smart_ingredient_split(test)
        print(f"Input:  {test}")
        print(f"Output: {result}")
        print(f"Count:  {len(result)} ingredients\n")
