"""
Explanation Generator

Converts reasoning results into human-friendly explanations.
Supports ELI5 mode and AI-powered follow-up generation.

INNOVATION: Adaptive explanation complexity for cognitive load reduction.
"""

import os
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
        language: str = "en"
    ) -> ExplanationOutput:
        """
        Main pipeline: Generate complete explanation package.
        
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
        
        # Detailed insights (formatted)
        detailed_insights = [
            f"{insight['icon']} **{insight['title']}**: {insight['explanation']}"
            for insight in reasoning_result["insights"]
        ]
        
        # Translate insights if needed
        if language != "en" and self.use_ai:
            detailed_insights = [self._translate_text(ins, language) for ins in detailed_insights]
        
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


# Singleton instance
explanation_generator = ExplanationGenerator()
