# FoodSense AI+ System Design

## Architecture Overview

FoodSense AI+ is a full-stack web application with a Python backend and Next.js frontend, designed to provide AI-native food ingredient analysis.

---

## High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                         User Interface                        │
│                     (Next.js + React)                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │  Home    │  │ Analyze  │  │ Compare  │  │ Timeline │    │
│  │  Page    │  │  Page    │  │  Page    │  │  Page    │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
└──────────────────────┬───────────────────────────────────────┘
                       │ HTTPS/REST API
                       ▼
┌──────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                          │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                   API Routes                           │  │
│  │  • POST /api/analyze                                   │  │
│  │  • POST /api/analyze/eli5                              │  │
│  │  • POST /api/compare                                   │  │
│  │  • POST /api/timeline                                  │  │
│  │  • GET  /api/demo-products                             │  │
│  └────────────────────────────────────────────────────────┘  │
│                           │                                   │
│  ┌────────────────────────┼────────────────────────────────┐ │
│  │            AI Processing Pipeline                       │ │
│  │                        ▼                                │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │  1. Intent Inference Engine                      │  │ │
│  │  │     • Food context detection                     │  │ │
│  │  │     • User intent inference (no config)          │  │ │
│  │  │     • Confidence scoring                         │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  │                        ▼                                │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │  2. Reasoning Engine                             │  │ │
│  │  │     • Ingredient matching (knowledge base)       │  │ │
│  │  │     • Prioritization by intent                   │  │ │
│  │  │     • Generate 3 insights                        │  │ │
│  │  │     • Health signal determination                │  │ │
│  │  │     • Trade-off extraction                       │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  │                        ▼                                │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │  3. Explanation Generator                        │  │ │
│  │  │     • Standard explanations                      │  │ │
│  │  │     • ELI5 mode (adaptive simplification)        │  │ │
│  │  │     • Follow-up question generation              │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  └─────────────────────────────────────────────────────────┘ │
│                           │                                   │
│  ┌────────────────────────┴────────────────────────────────┐ │
│  │          Optional: OpenAI / Gemini API                  │ │
│  │          (ELI5 mode & follow-up generation)             │ │
│  └─────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│               Ingredient Knowledge Base                       │
│              (Python Module - In-Memory)                      │
│  • 15+ curated ingredients with research data                │
│  • Health impacts, concerns, benefits                        │
│  • Research confidence levels                                │
│  • Safe consumption limits                                   │
└──────────────────────────────────────────────────────────────┘
```

---

## Component Details

### Frontend (Next.js)

**Technology Stack**:
- Next.js 14 (React 18)
- TypeScript
- TailwindCSS
- Axios (API calls)
- Lucide Icons

**Pages**:
1. **index.tsx** (Home)
   - Ingredient input (text/paste)
   - Demo product selection
   - Voice input integration (future)
   - CTA to analyze

2. **analyze.tsx** (Results)
   - Health signal display
   - Confidence visualization
   - 3 insight cards
   - Trade-offs section
   - Uncertainty note
   - ELI5 toggle
   - AI-generated follow-ups

**Components**:
- **InsightCard**: Displays single insight with icon, title, explanation
- **HealthSignal**: 🟢🟡🔴 visual indicator with description
- **ConfidenceBar**: Progress bar showing research confidence
- **VoiceInput**: Web Speech API integration for voice commands

---

### Backend (FastAPI)

**Technology Stack**:
- Python 3.11+
- FastAPI
- Pydantic (data validation)
- OpenAI SDK / Google Gemini (optional)
- Python-dotenv

**API Endpoints**:

#### 1. POST `/api/analyze`
**Request**:
```json
{
  "ingredients": ["sugar", "wheat flour", "red 40"],
  "product_name": "Cookie",
  "user_question": null,
  "include_eli5": false
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "context": {
      "food_type": "baked_good",
      "detected_intent": "general_health",
      "summary": "This appears to be a baked good..."
    },
    "insights": [...],
    "health_signal": {
      "level": "moderate_concern",
      "confidence": "medium",
      "icon": "🟡"
    },
    "trade_offs": {...},
    "uncertainty_note": "...",
    "follow_up_questions": [...]
  }
}
```

#### 2. POST `/api/analyze/eli5`
Returns simplified explanation only.

#### 3. GET `/api/demo-products`
Returns pre-configured demo products for testing.

---

### AI Processing Pipeline

#### 1. Intent Inference Engine
**File**: `backend/ai/intent_inference.py`

**Purpose**: Automatically detect user health priorities

**Process**:
1. Analyze food context (snack, beverage, cereal, etc.)
2. Detect ingredient concern patterns
3. Infer primary intent:
   - General health
   - Weight management
   - Child safety
   - Athletic performance
   - Long-term health
   - Ingredient transparency

**Output**:
```python
{
  "food_context": "packaged_snack",
  "primary_intent": "general_health",
  "context_summary": "This appears to be a packaged snack...",
  "confidence": 0.85
}
```

---

#### 2. Reasoning Engine
**File**: `backend/ai/reasoning_engine.py`

**Purpose**: Generate exactly 3 actionable insights

**Process**:
1. **Match ingredients**: Lookup in knowledge base
2. **Prioritize**: Score ingredients by:
   - Number of health concerns
   - Research confidence
   - Relevance to user intent
   - Ingredient abundance (list position)
3. **Generate insights**: Top 3 only
4. **Determine health signal**: 🟢 🟡 🔴
5. **Extract trade-offs**: Benefits vs downsides
6. **Add uncertainty note**: Honest communication

**Output**:
```python
{
  "overall_signal": "moderate_concern",
  "overall_confidence": "medium",
  "insights": [
    {
      "title": "Sugar – Potential Concern",
      "explanation": "High consumption linked to...",
      "concern_level": "negative",
      "confidence": "high",
      "icon": "⚠️"
    },
    ...
  ],
  "trade_offs": {
    "benefits": [...],
    "downsides": [...]
  },
  "uncertainty_note": "..."
}
```

---

#### 3. Explanation Generator
**File**: `backend/ai/explanation_generator.py`

**Purpose**: Convert reasoning into human-friendly text

**Modes**:
1. **Standard Mode**: Technical accuracy
2. **ELI5 Mode**: 10-year-old comprehension

**Process**:
1. Generate summary sentence
2. Format insights as cards
3. (Optional) Call AI API for ELI5 transformation
4. Generate 4 follow-up questions

**ELI5 Transformation**:
- "metabolic" → "how your body uses energy"
- "cardiovascular" → "heart"
- "hyperactivity" → "extra energy"
- Sentence length: max 15 words

---

### Ingredient Knowledge Base
**File**: `backend/utils/mock_ingredient_data.py`

**Structure**:
```python
{
  "ingredient_name": {
    "name": "Display Name",
    "category": "sweetener | preservative | ...",
    "health_impact": "Summary",
    "research_confidence": "high | medium | low",
    "concerns": ["List of concerns"],
    "benefits": ["List of benefits"],
    "safe_limit": "WHO/FDA guidance",
    "common_in": ["Food types"]
  }
}
```

**Current Coverage**: 15+ ingredients
- Sugars: sugar, HFCS, aspartame
- Preservatives: sodium benzoate, BHT, potassium sorbate
- Additives: MSG, Red 40, Yellow 5
- Fats: palm oil, partially hydrogenated oil, olive oil
- Natural: whole wheat, oats, whey protein

---

## Data Flow

```
User Input
   │
   ├─ Ingredients: ["sugar", "red 40", "bht"]
   ├─ Product Name: "Cereal"
   └─ User Question: null
         │
         ▼
┌────────────────────────────┐
│  Intent Inference          │
│  Detects: breakfast_cereal │
│  Intent: long_term_health  │
└────────┬───────────────────┘
         ▼
┌────────────────────────────┐
│  Reasoning Engine          │
│  Matches ingredients       │
│  Prioritizes by intent     │
│  Generates 3 insights      │
└────────┬───────────────────┘
         ▼
┌────────────────────────────┐
│  Explanation Generator     │
│  Formats output            │
│  Optional: ELI5            │
└────────┬───────────────────┘
         ▼
    JSON Response
         ▼
    Frontend Render
```

---

## Innovation Features

### 1. Voice Input
**File**: `frontend/components/VoiceInput.tsx`

Uses Web Speech API (browser-native):
- Continuous listening mode
- Real-time transcription
- Auto-population of ingredient field

### 2. Product Comparison
**File**: `backend/ai/product_comparison.py`

Compares 2-3 products side-by-side:
- Determines best choice
- Highlights key differences
- Explains trade-offs

### 3. Impact Timeline
**File**: `backend/ai/impact_timeline.py`

Projects cumulative health effects:
- 1 day, 1 week, 1 month horizons
- Extrapolates based on consumption frequency
- Severity scaling over time

---

## Deployment Architecture

### Development
```
Local Machine
├─ Backend:  http://localhost:8000
└─ Frontend: http://localhost:3000
```

### Production (Recommended)
```
┌─────────────────────┐
│  Vercel (Frontend)  │
│  • Next.js auto     │
│  • CDN              │
│  • Edge functions   │
└─────────┬───────────┘
          │ API calls
          ▼
┌─────────────────────┐
│  Railway (Backend)  │
│  • Python FastAPI   │
│  • Auto-deploy      │
│  • Custom domain    │
└─────────────────────┘
```

**Alternative Backends**:
- Render
- Heroku
- AWS Lambda (serverless)
- Google Cloud Run

---

## Security Considerations

1. **API Keys**: Store in `.env`, never commit
2. **CORS**: Configure allowed origins
3. **Rate Limiting**: Prevent API abuse
4. **Input Validation**: Pydantic models
5. **Sanitization**: Prevent injection attacks

---

## Scalability Considerations

### Current MVP
- In-memory ingredient database
- Synchronous API calls
- No caching

### Production Enhancements
1. **Database**: PostgreSQL for ingredients
2. **Caching**: Redis for frequent queries
3. **Queue**: Celery for async processing
4. **CDN**: CloudFront for static assets
5. **Monitoring**: Sentry for error tracking

---

## Testing Strategy

### Backend
- Unit tests: pytest
- API tests: pytest + httpx
- Coverage target: 80%

### Frontend
- Component tests: Jest + React Testing Library
- E2E tests: Playwright
- Visual regression: Percy

---

## Future Enhancements

1. **OCR Integration**: Tesseract for label scanning
2. **User Accounts**: Save analysis history
3. **Personalization**: Learn from user preferences
4. **Barcode Scanning**: Direct product lookup
5. **Nutrition Database**: OpenFoodFacts API
6. **Multi-Language**: i18n support
7. **Mobile Apps**: React Native
8. **Offline Mode**: PWA capabilities

---

## Development Workflow

1. **Setup**: Clone repo, install dependencies
2. **Backend**: Start with `uvicorn app:app --reload`
3. **Frontend**: Start with `npm run dev`
4. **Test**: Use demo products
5. **Deploy**: Push to main branch (auto-deploy)

---

## Code Organization

```
FoodSence/
├─ backend/
│  ├─ app.py                    # FastAPI entry point
│  ├─ routes/
│  │  └─ analyze_food.py        # API endpoints
│  ├─ ai/
│  │  ├─ intent_inference.py    # Core innovation
│  │  ├─ reasoning_engine.py    # Insight generation
│  │  ├─ explanation_generator.py
│  │  ├─ product_comparison.py
│  │  └─ impact_timeline.py
│  └─ utils/
│     └─ mock_ingredient_data.py
│
├─ frontend/
│  ├─ pages/
│  │  ├─ index.tsx              # Home
│  │  └─ analyze.tsx            # Results
│  ├─ components/
│  │  ├─ InsightCard.tsx
│  │  ├─ HealthSignal.tsx
│  │  ├─ ConfidenceBar.tsx
│  │  └─ VoiceInput.tsx
│  └─ styles/
│     └─ globals.css
│
└─ docs/
   ├─ system_design.md          # This file
   ├─ patent_abstract.md
   └─ demo_script.md
```

---

## Performance Metrics

**Target Response Times**:
- Intent inference: < 50ms
- Reasoning engine: < 200ms
- Explanation generation: < 500ms (no AI) / < 2s (with AI)
- Total API response: < 3s

**Optimization Strategies**:
- Parallel processing
- Lazy AI loading
- Response caching
- Ingredient preloading

---

This system design prioritizes **user experience** over technical complexity, ensuring that the AI-native interface remains the central focus.
