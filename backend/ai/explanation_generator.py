"""
Explanation Generator

Converts reasoning results into human-friendly explanations.
Supports ELI5 mode and AI-powered follow-up generation.

INNOVATION: Adaptive explanation complexity for cognitive load reduction.
"""

import os
import time
from typing import List, Dict, Optional
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()


class FollowUpQuestion(BaseModel):
    """AI-generated follow-up question."""
    question: str
    context: str  # Why this question is relevant


class ExplanationOutput(BaseModel):
    """Complete explanation package."""
    summary: str
    detailed_insights: List[str]
    eli5_explanation: Optional[str]
    follow_up_questions: List[FollowUpQuestion]


class ExplanationGenerator:
    """
    Generates human-friendly explanations from reasoning results.
    """
    
    def __init__(self):
        self.ai_provider = os.getenv("AI_PROVIDER", "gemini")
        self.ai_model = os.getenv("AI_MODEL", "gemini-pro")
        
        # Initialize AI client (optional for MVP - can use rule-based)
        self.use_ai = False
        
        try:
            if self.ai_provider == "gemini":
                import google.generativeai as genai
                genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
                self.model = genai.GenerativeModel(self.ai_model)
                self.use_ai = True
                print(f"✅ Gemini AI initialized: {self.ai_model}")
                
            elif self.ai_provider == "groq":
                from groq import Groq
                self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
                self.use_ai = True
                print(f"✅ Groq AI initialized: {self.ai_model}")
                
            elif self.ai_provider == "deepseek":
                import openai
                self.client = openai.OpenAI(
                    api_key=os.getenv("DEEPSEEK_API_KEY"),
                    base_url="https://api.deepseek.com"
                )
                self.use_ai = True
                print(f"✅ DeepSeek AI initialized: {self.ai_model}")
                
        except Exception as e:
            print(f"⚠️ AI initialization failed: {e}. Using rule-based fallback.")
            self.use_ai = False
    
    def _call_ai_with_retry(self, prompt: str, max_retries: int = 3) -> str:
        """
        Call AI with retry logic and multi-provider fallback.
        Tries: Primary Provider → Groq → DeepSeek
        """
        last_error = None
        
        for attempt in range(max_retries):
            try:
                # Try primary provider
                if self.ai_provider == "gemini" and hasattr(self, 'model'):
                    # Configure request with timeout
                    generation_config = {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "top_k": 40,
                        "max_output_tokens": 8192,
                    }
                    
                    safety_settings = [
                        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                    ]
                    
                    response = self.model.generate_content(
                        prompt,
                        generation_config=generation_config,
                        safety_settings=safety_settings
                    )
                    return response.text
                    
                elif self.ai_provider == "groq" and hasattr(self, 'client'):
                    response = self.client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model=self.ai_model
                    )
                    return response.choices[0].message.content
                    
                elif self.ai_provider == "deepseek" and hasattr(self, 'client'):
                    response = self.client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model=self.ai_model
                    )
                    return response.choices[0].message.content
                    
            except Exception as e:
                last_error = e
                print(f"⚠️ Attempt {attempt + 1}/{max_retries} failed: {str(e)[:200]}")
                
                if attempt < max_retries - 1:
                    wait_time = min(2 ** attempt, 5)  # Max 5 seconds wait
                    print(f"⏳ Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"❌ All {max_retries} attempts exhausted")
        
        # All retries failed - try fallback providers
        print("🔄 Primary provider failed, trying fallback providers...")
        
        # Try Groq as fallback
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key and self.ai_provider != "groq":
            try:
                print("🔄 Trying Groq fallback...")
                from groq import Groq
                client = Groq(api_key=groq_key)
                response = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.1-70b-versatile"
                )
                print("✅ Groq fallback succeeded")
                return response.choices[0].message.content
            except Exception as e:
                print(f"⚠️ Groq fallback failed: {e}")
        
        # Try DeepSeek as final fallback
        deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        if deepseek_key and self.ai_provider != "deepseek":
            try:
                print("🔄 Trying DeepSeek fallback...")
                import openai
                client = openai.OpenAI(
                    api_key=deepseek_key,
                    base_url="https://api.deepseek.com"
                )
                response = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="deepseek-chat"
                )
                print("✅ DeepSeek fallback succeeded")
                return response.choices[0].message.content
            except Exception as e:
                print(f"⚠️ DeepSeek fallback failed: {e}")
        
        raise Exception(f"All AI providers failed. Last error: {last_error}")
    
    def _get_language_instruction(self, language: str) -> str:
        """Get language-specific instruction for AI prompts."""
        language_names = {
            "en": "English",
            "hi": "Hindi (हिन्दी)",
            "bn": "Bengali (বাংলা)",
            "ta": "Tamil (தமிழ்)",
            "te": "Telugu (తెలుగు)",
            "mr": "Marathi (मराठी)",
            "gu": "Gujarati (ગુજરાતી)",
            "kn": "Kannada (ಕನ್ನಡ)",
            "ml": "Malayalam (മലയാളം)",
            "pa": "Punjabi (ਪੰਜਾਬੀ)"
        }
        lang_name = language_names.get(language, "English")
        return f"\n\nIMPORTANT: Respond in {lang_name}. Use native script and natural language."
    
    def _translate_text(self, text: str, language: str) -> str:
        """Translate text to target language using AI."""
        if not self.use_ai or language == "en":
            return text
        
        try:
            lang_instruction = self._get_language_instruction(language)
            prompt = f"Translate the following text to the target language. Preserve formatting and meaning:\n\n{text}{lang_instruction}"
            
            if self.ai_provider == "gemini":
                response = self.model.generate_content(prompt)
                return response.text
            elif self.ai_provider == "groq":
                response = self.client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=self.ai_model
                )
                return response.choices[0].message.content
            elif self.ai_provider == "deepseek":
                response = self.client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=self.ai_model
                )
                return response.choices[0].message.content
        except Exception as e:
            print(f"⚠️ Translation failed: {e}")
            return text  # Return original if translation fails
    
    def _translate_followups(self, followups: List[FollowUpQuestion], language: str) -> List[FollowUpQuestion]:
        """Translate follow-up questions to target language."""
        if not self.use_ai or language == "en":
            return followups
        
        translated = []
        for fq in followups:
            translated.append(FollowUpQuestion(
                question=self._translate_text(fq.question, language),
                context=self._translate_text(fq.context, language)
            ))
        return translated
    
    def generate_summary(
        self,
        overall_signal: str,
        confidence: str,
        context_summary: str
    ) -> str:
        """
        Generate a one-sentence summary.
        """
        signal_descriptions = {
            "likely_safe": "appears relatively safe for moderate consumption",
            "moderate_concern": "has some ingredients worth being aware of",
            "potential_risk": "contains ingredients that may warrant caution"
        }
        
        signal_text = signal_descriptions.get(overall_signal, "has mixed characteristics")
        
        return f"{context_summary} This product {signal_text}."
    
    def generate_eli5_explanation(
        self,
        insights: List[Dict],
        trade_offs: Dict[str, List[str]]
    ) -> str:
        """
        Generate Explain-Like-I'm-5 version.
        
        Uses simple words, short sentences, no jargon.
        """
        if self.use_ai:
            return self._generate_eli5_with_ai(insights, trade_offs)
        else:
            return self._generate_eli5_rule_based(insights, trade_offs)
    
    def _generate_eli5_rule_based(
        self,
        insights: List[Dict],
        trade_offs: Dict[str, List[str]]
    ) -> str:
        """
        Rule-based ELI5 (fallback when AI unavailable).
        """
        lines = []
        lines.append("Let me explain this simply:")
        lines.append("")
        
        # Simplify each insight
        for idx, insight in enumerate(insights[:3], 1):
            title = insight.get("title", "")
            explanation = insight.get("explanation", "")
            
            # Skip if it's a "limited information" placeholder
            if "Limited Information" in title or "not in our database" in explanation:
                continue
            
            # Extract ingredient name
            if "–" in title:
                ingredient = title.split("–")[0].strip()
            else:
                ingredient = title.strip()
            
            # Simplification rules
            simple = explanation.lower()
            simple = simple.replace("metabolic", "how your body uses energy")
            simple = simple.replace("cardiovascular", "heart and blood vessels")
            simple = simple.replace("hyperactivity", "being extra energetic or restless")
            simple = simple.replace("endocrine", "hormones")
            simple = simple.replace("carcinogen", "something that might cause cancer")
            simple = simple.replace("consumption", "eating")
            simple = simple.replace("excessive", "too much")
            simple = simple.replace("linked to", "connected to")
            simple = simple.replace("associated with", "connected to")
            
            # Capitalize first letter
            if simple:
                simple = simple[0].upper() + simple[1:]
            
            lines.append(f"{idx}. **{ingredient}**: {simple[:200]}")
        
        lines.append("")
        
        # Smart summary based on trade-offs
        downsides_count = len(trade_offs.get("downsides", []))
        benefits_count = len(trade_offs.get("benefits", []))
        
        if downsides_count == 0:
            summary = "✅ This food looks pretty good! Enjoy it as part of a balanced diet."
        elif downsides_count < 2 and benefits_count > 0:
            summary = "✅ Mostly okay to have sometimes. Just don't eat it every single day."
        elif downsides_count >= 3:
            summary = "⚠️ Best to have just once in a while as a treat, not every day."
        else:
            summary = "⚖️ Has some good parts and some not-so-good parts. Moderation is key!"
        
        lines.append("**In short**: " + summary)
        
        return "\n".join(lines)
    
    def _generate_eli5_with_ai(
        self,
        insights: List[Dict],
        trade_offs: Dict[str, List[str]]
    ) -> str:
        """
        AI-powered ELI5 generation (GPT-4 or Gemini).
        """
        prompt = f"""
Explain these food ingredient insights like I'm 10 years old.

Insights:
{insights}

Trade-offs:
Benefits: {trade_offs.get('benefits', [])}
Downsides: {trade_offs.get('downsides', [])}

Requirements:
- Use very simple words
- Short sentences (max 15 words each)
- No scientific terms
- Be honest about good and bad parts
- Make it friendly and clear

Limit to 4-5 sentences total.
"""
        
        try:
            if self.ai_provider == "gemini":
                response = self.model.generate_content(prompt)
                return response.text.strip()
            
            elif self.ai_provider == "groq":
                response = self.client.chat.completions.create(
                    model=self.ai_model,
                    messages=[
                        {"role": "system", "content": "You explain food ingredients to children in simple, clear language."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=200
                )
                return response.choices[0].message.content.strip()
            
            elif self.ai_provider == "deepseek":
                response = self.client.chat.completions.create(
                    model=self.ai_model,
                    messages=[
                        {"role": "system", "content": "You explain food ingredients to children in simple, clear language."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=200
                )
                return response.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"⚠️ AI generation failed: {e}")
            return self._generate_eli5_rule_based(insights, trade_offs)
    
    def generate_follow_up_questions(
        self,
        insights: List[Dict],
        food_context: str,
        intent: str
    ) -> List[FollowUpQuestion]:
        """
        Generate 3-4 relevant follow-up questions.
        
        These are AI-generated based on the analysis.
        """
        if self.use_ai:
            return self._generate_followups_with_ai(insights, food_context, intent)
        else:
            return self._generate_followups_rule_based(food_context, intent)
    
    def _generate_followups_rule_based(
        self,
        food_context: str,
        intent: str
    ) -> List[FollowUpQuestion]:
        """
        Rule-based follow-up questions (template-based).
        """
        questions = [
            FollowUpQuestion(
                question="Is this safe for kids?",
                context="Children may be more sensitive to certain additives"
            ),
            FollowUpQuestion(
                question="Can I eat this daily?",
                context="Frequency of consumption affects health impact"
            ),
            FollowUpQuestion(
                question="What are healthier alternatives?",
                context="Similar products with better ingredient profiles"
            ),
            FollowUpQuestion(
                question="What if I'm trying to lose weight?",
                context="Weight management considerations"
            )
        ]
        
        # Context-specific additions
        if "snack" in food_context or "candy" in food_context:
            questions.insert(2, FollowUpQuestion(
                question="How much is too much?",
                context="Portion control and safe consumption limits"
            ))
        
        if "beverage" in food_context:
            questions.insert(1, FollowUpQuestion(
                question="What about the sugar content?",
                context="Beverages often contain hidden sugars"
            ))
        
        return questions[:4]  # Return top 4
    
    def _generate_followups_with_ai(
        self,
        insights: List[Dict],
        food_context: str,
        intent: str
    ) -> List[FollowUpQuestion]:
        """
        AI-powered follow-up generation.
        """
        prompt = f"""
Based on this food analysis, generate 4 relevant follow-up questions a user might ask.

Food Context: {food_context}
User Intent: {intent}
Key Insights: {insights}

Generate questions that:
- Are natural and conversational
- Help the user understand health impacts better
- Are specific to this product type
- Address common concerns

Return as JSON array:
[
  {{"question": "...", "context": "..."}},
  {{"question": "...", "context": "..."}}
]
"""
        
        try:
            import json
            
            if self.ai_provider == "gemini":
                response = self.model.generate_content(prompt)
                result = json.loads(response.text)
                return [FollowUpQuestion(**q) for q in result]
            
            elif self.ai_provider == "groq":
                response = self.client.chat.completions.create(
                    model=self.ai_model,
                    messages=[
                        {"role": "system", "content": "You generate helpful follow-up questions about food ingredients."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.8,
                    max_tokens=300
                )
                result = json.loads(response.choices[0].message.content)
                return [FollowUpQuestion(**q) for q in result]
            
            elif self.ai_provider == "deepseek":
                response = self.client.chat.completions.create(
                    model=self.ai_model,
                    messages=[
                        {"role": "system", "content": "You generate helpful follow-up questions about food ingredients."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.8,
                    max_tokens=300
                )
                result = json.loads(response.choices[0].message.content)
                return [FollowUpQuestion(**q) for q in result]
        
        except Exception as e:
            print(f"⚠️ AI follow-up generation failed: {e}")
            return self._generate_followups_rule_based(food_context, intent)
    
    def generate_complete_explanation(
        self,
        reasoning_result: Dict,
        intent_result: Dict,
        include_eli5: bool = False,
        language: str = "en",
        original_ingredients: List[str] = None
    ) -> ExplanationOutput:
        """
        Main pipeline: Generate complete explanation package with DETAILED ingredient breakdown.
        
        Supports multi-language output for Indian languages.
        """
        # Get language suffix for prompts
        language_instruction = self._get_language_instruction(language)
        
        # Summary
        summary = self.generate_summary(
            reasoning_result["overall_signal"],
            reasoning_result["overall_confidence"],
            intent_result["context_summary"]
        )
        
        # If non-English, translate summary
        if language != "en" and self.use_ai:
            summary = self._translate_text(summary, language)
        
        # Generate DETAILED insights for ALL ingredients using AI
        detailed_insights = self._generate_detailed_ingredient_analysis(
            reasoning_result["insights"],
            language,
            original_ingredients
        )
        
        # ELI5 (optional)
        eli5 = None
        if include_eli5:
            eli5 = self.generate_eli5_explanation(
                reasoning_result["insights"],
                reasoning_result["trade_offs"]
            )
            if language != "en" and self.use_ai and eli5:
                eli5 = self._translate_text(eli5, language)
        
        # Follow-ups
        follow_ups = self.generate_follow_up_questions(
            reasoning_result["insights"],
            intent_result["food_context"],
            intent_result["primary_intent"]
        )
        
        # Translate follow-ups if needed
        if language != "en" and self.use_ai:
            follow_ups = self._translate_followups(follow_ups, language)
        
        return ExplanationOutput(
            summary=summary,
            detailed_insights=detailed_insights,
            eli5_explanation=eli5,
            follow_up_questions=follow_ups
        )
    
    def _generate_detailed_ingredient_analysis(
        self,
        insights: List[Dict],
        language: str = "en",
        original_ingredients: List[str] = None
    ) -> List[str]:
        """
        Generate comprehensive analysis for EVERY ingredient using AI.
        Uses original ingredient list to ensure ALL ingredients are analyzed.
        """
        if not self.use_ai:
            # Fallback to basic formatting
            return [
                f"{insight['icon']} **{insight['title']}**: {insight['explanation']}"
                for insight in insights
            ]
        
        # USE ORIGINAL INGREDIENT LIST if provided (bypasses mock database limitations)
        if original_ingredients and len(original_ingredients) > 0:
            all_ingredients = [{"name": ing.strip()} for ing in original_ingredients]
            print(f"📝 Analyzing {len(all_ingredients)} ingredients from original list")
        else:
            # Fallback: Extract from insights
            all_ingredients = []
            for insight in insights:
                title = insight.get("title", "")
                if "–" in title:
                    ingredient = title.split("–")[0].strip()
                else:
                    ingredient = title.strip().replace("Limited Information", "").strip()
                
                if ingredient and ingredient != "":
                    all_ingredients.append({"name": ingredient})
        
        if not all_ingredients:
            return []
        
        # Build comprehensive prompt for AI - analyze ALL ingredients
        lang_instruction = self._get_language_instruction(language)
        
        print(f"🔍 Starting AI analysis for {len(all_ingredients)} ingredients")
        print(f"📋 Ingredient list: {[ing['name'] for ing in all_ingredients][:10]}")
        
        prompt = f"""You are a food safety and nutrition expert analyzing ingredients for a consumer health app.

TASK: Provide COMPLETE, DETAILED analysis for EVERY SINGLE ingredient below.

INGREDIENT LIST (Total: {len(all_ingredients)}):
{chr(10).join([f"{i+1}. {ing['name']}" for i, ing in enumerate(all_ingredients)])}

CRITICAL REQUIREMENTS:
✓ Analyze ALL {len(all_ingredients)} ingredients above (count them in your response)
✓ Do NOT skip any ingredient, even if common (butter, eggs, sugar, etc.)
✓ Use this EXACT format for EACH ingredient:

### [Full Ingredient Name]
**What it is**: [1-2 sentences: common name, E-code if applicable, category (preservative/sweetener/etc.)]
**Health Effects**: 
  - ✅ Benefits: [List 2-3 specific health benefits, or \"Primarily functional\" if minimal]
  - ⚠️ Concerns: [List 2-3 specific health concerns, or \"None known at normal levels\"]
**Safety**: [FDA/FSSAI approval status, safe daily limits if known, who should avoid]
**Usage in Food**: [Why manufacturers use it, what products commonly contain it]
**Final Verdict**: [Choose ONE: ✅ Generally Safe | ⚠️ Use Moderately | ❌ Limit/Avoid] + [1 sentence explanation]

---

EXAMPLE FORMAT:
### Butter
**What it is**: Natural dairy fat from cow's milk, rich in saturated fats and fat-soluble vitamins A, D, E, K.
**Health Effects**: 
  - ✅ Benefits: Contains vitamins A, D, E, K; provides energy; natural source of conjugated linoleic acid (CLA)
  - ⚠️ Concerns: High in saturated fat (7g per tbsp); excessive intake linked to elevated LDL cholesterol
**Safety**: FSSAI approved; safe in moderation (1-2 tablespoons/day); avoid if lactose intolerant or dairy allergic
**Usage in Food**: Adds rich flavor, moisture, and tender texture to baked goods; traditional cooking fat
**Final Verdict**: ⚠️ Use Moderately - Enjoy in small amounts as part of a balanced diet; saturated fat content requires moderation

---

NOW ANALYZE ALL {len(all_ingredients)} INGREDIENTS ABOVE IN THIS EXACT FORMAT.
Do not summarize or group ingredients - each needs individual analysis.{lang_instruction}"""

        try:
            # Try AI with retry logic and fallback providers (2 attempts max)
            full_analysis = self._call_ai_with_retry(prompt, max_retries=2)
            
            if not full_analysis or len(full_analysis.strip()) < 50:
                raise Exception(f"AI returned empty or too short response: {len(full_analysis)} chars")
            
            print(f"✅ AI response received: {len(full_analysis)} characters")
            
            # Split by ingredient headings
            detailed_insights = []
            sections = full_analysis.split("###")
            for section in sections[1:]:  # Skip first empty section
                section = section.strip()
                if section:
                    detailed_insights.append("### " + section)
            
            # Validate response quality
            expected_count = len(all_ingredients)
            actual_count = len(detailed_insights)
            
            print(f"📊 Analysis results: {actual_count}/{expected_count} ingredients")
            
            if actual_count == 0:
                print("⚠️ WARNING: No ingredient sections found in AI response")
                print(f"📄 Response preview: {full_analysis[:500]}...")
                # Return full response as fallback
                return [f"### Complete Analysis\n{full_analysis}"]
            
            if actual_count < expected_count * 0.7:  # Less than 70%
                print(f"⚠️ WARNING: Only {actual_count}/{expected_count} ingredients analyzed ({actual_count/expected_count*100:.0f}%)")
                print(f"Missing: {expected_count - actual_count} ingredients")
            else:
                print(f"✅ SUCCESS: {actual_count}/{expected_count} ingredients analyzed ({actual_count/expected_count*100:.0f}%)")
            
            return detailed_insights
            
        except Exception as e:
            print(f"❌ CRITICAL: Detailed analysis failed: {e}")
            import traceback
            traceback.print_exc()
            
            # Structured fallback analysis
            print(f"🔄 Creating structured fallback for {len(all_ingredients)} ingredients")
            fallback_analyses = []
            
            for ing in all_ingredients:
                name = ing['name']
                fallback_analyses.append(f"""### {name}
**What it is**: {name} - a food ingredient (detailed analysis temporarily unavailable)
**Health Effects**: 
  - ✅ Benefits: Contains nutritional or functional properties
  - ⚠️ Concerns: Moderation advised for processed ingredients; consult labels
**Safety**: Generally recognized as safe (GRAS) when used as directed by manufacturers
**Usage in Food**: Common ingredient in packaged food products for taste, texture, or preservation
**Final Verdict**: ⚠️ Use Moderately - Safe in normal amounts; check product labels for specifics

*Note: Comprehensive AI analysis failed. This is a basic safety overview. For detailed information, consult food safety databases.*
---""")
            
            print(f"✅ Generated {len(fallback_analyses)} fallback analyses")
            return fallback_analyses


# Singleton instance
explanation_generator = ExplanationGenerator()
