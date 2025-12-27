# FoodSense AI+ Setup Guide

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Python 3.11 or higher
- Node.js 18 or higher
- npm or yarn
- Git (optional)

---

## Step 1: Clone/Download Project

```bash
cd Desktop
cd FoodSence
```

---

## Step 2: Backend Setup

### Navigate to backend folder
```bash
cd backend
```

### Create virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### Install dependencies
```bash
pip install -r requirements.txt
```

### Configure environment variables
```bash
# Copy example env file
copy .env.example .env  # Windows
cp .env.example .env    # Mac/Linux
```

### Edit `.env` file
Open `backend/.env` and add your AI API key:

```env
# Choose ONE:

# Option 1: OpenAI (Recommended for best results)
AI_PROVIDER=openai
AI_MODEL=gpt-4
OPENAI_API_KEY=sk-your-key-here

# Option 2: Google Gemini (Free tier available)
AI_PROVIDER=gemini
AI_MODEL=gemini-1.5-pro
GOOGLE_API_KEY=your-gemini-key-here

# Option 3: No AI (Rule-based fallback - works without API key)
# Just leave keys empty, system will use rule-based mode
```

### Start backend server
```bash
uvicorn app:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Test backend (in new terminal)
```bash
# Visit in browser:
http://localhost:8000

# Should see:
{"message": "FoodSense AI+ API is running", "status": "healthy"}
```

---

## Step 3: Frontend Setup

### Open NEW terminal, navigate to frontend
```bash
cd Desktop\FoodSence\frontend  # Windows
cd Desktop/FoodSence/frontend  # Mac/Linux
```

### Install dependencies
```bash
npm install
```

### Configure environment
```bash
# Copy example env
copy .env.example .env.local  # Windows
cp .env.example .env.local    # Mac/Linux
```

### Edit `.env.local`
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Start frontend
```bash
npm run dev
```

You should see:
```
ready - started server on 0.0.0.0:3000
```

---

## Step 4: Test the Application

1. Open browser: `http://localhost:3000`
2. Click "🥣 Sugar Cereal" demo
3. Click "Analyze with AI"
4. Should see results within 3 seconds

---

## ✅ Verification Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] Demo products load
- [ ] Analysis works
- [ ] Health signal shows
- [ ] 3 insights appear
- [ ] ELI5 button works (if AI enabled)

---

## 🛠️ Troubleshooting

### Backend Issues

**Problem**: `ModuleNotFoundError: No module named 'fastapi'`
```bash
# Solution: Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Then reinstall
pip install -r requirements.txt
```

**Problem**: `uvicorn: command not found`
```bash
# Solution: Install uvicorn directly
pip install uvicorn
```

**Problem**: Port 8000 already in use
```bash
# Solution: Use different port
uvicorn app:app --reload --port 8001

# Update frontend .env.local:
NEXT_PUBLIC_API_URL=http://localhost:8001
```

---

### Frontend Issues

**Problem**: `npm: command not found`
```bash
# Solution: Install Node.js from nodejs.org
# Then retry npm install
```

**Problem**: Port 3000 already in use
```bash
# Solution: Next.js will auto-suggest port 3001
# Or specify port:
npm run dev -- -p 3001
```

**Problem**: `axios` errors / CORS
```bash
# Solution: Check backend is running
# Check .env.local has correct API_URL
```

---

### AI API Issues

**Problem**: "Analysis failed" errors
```bash
# Solution 1: Check API key is valid
# - OpenAI: https://platform.openai.com/api-keys
# - Gemini: https://ai.google.dev/

# Solution 2: Use rule-based mode (no API key needed)
# Leave AI keys empty in .env
```

**Problem**: Slow ELI5 generation
```bash
# This is normal - AI calls take 2-5 seconds
# Rule-based mode is instant but less sophisticated
```

---

## 🎯 Getting API Keys

### OpenAI (GPT-4)
1. Go to https://platform.openai.com/
2. Sign up / Log in
3. Navigate to API Keys
4. Create new secret key
5. Copy to `.env` file

**Cost**: ~$0.03 per analysis (GPT-4)  
**Free tier**: $5 credit for new accounts

### Google Gemini
1. Go to https://ai.google.dev/
2. Get API key (free)
3. Copy to `.env` file

**Cost**: Free tier available  
**Limits**: Generous for hackathon use

### No API Key (Rule-Based)
- Just leave keys empty
- System uses template-based responses
- Faster but less sophisticated

---

## 📦 Project Structure

```
FoodSence/
├─ backend/           # Python FastAPI server
│  ├─ app.py          # Main entry point
│  ├─ requirements.txt
│  └─ .env            # Your API keys HERE
│
├─ frontend/          # Next.js React app
│  ├─ pages/
│  ├─ components/
│  ├─ package.json
│  └─ .env.local      # API URL HERE
│
├─ docs/              # Documentation
└─ README.md
```

---

## 🚀 Deployment (Optional)

### Backend: Railway

1. Go to https://railway.app/
2. Sign up with GitHub
3. New Project → Deploy from GitHub
4. Select `FoodSence` repo
5. Set root directory: `backend`
6. Add environment variables
7. Deploy

### Frontend: Vercel

1. Go to https://vercel.com/
2. Sign up with GitHub
3. New Project → Import `FoodSence`
4. Set root directory: `frontend`
5. Add environment variable:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend.railway.app
   ```
6. Deploy

**Result**: Live hackathon demo!

---

## 🎥 Recording Demo Video

1. **Start both servers** (backend + frontend)
2. **Open browser** to `http://localhost:3000`
3. **Start screen recording**:
   - Windows: Xbox Game Bar (Win+G)
   - Mac: QuickTime Player
   - Cross-platform: OBS Studio

4. **Follow demo script** (see `docs/demo_script.md`)
5. **Edit** with CapCut or iMovie
6. **Upload** to YouTube/Google Drive

---

## 📝 Adding More Ingredients

Edit `backend/utils/mock_ingredient_data.py`:

```python
INGREDIENT_DATABASE = {
    "your_ingredient": IngredientInfo(
        name="Display Name",
        category="sweetener",
        health_impact="Short description",
        research_confidence="medium",
        concerns=["List concerns"],
        benefits=["List benefits"],
        safe_limit="WHO guidance",
        common_in=["Foods"]
    ),
    # ... existing ingredients
}
```

Restart backend to see changes.

---

## 🔧 Development Tips

### Hot Reload
- Backend: Auto-reloads on file save
- Frontend: Auto-reloads on file save
- Just edit and refresh browser

### Debugging
```bash
# Backend logs appear in terminal
# Frontend logs: Browser console (F12)
```

### Testing Changes
1. Edit code
2. Save file
3. Refresh browser
4. See changes instantly

---

## 🏆 Hackathon Submission Checklist

- [ ] Code pushed to GitHub
- [ ] README.md complete
- [ ] Backend deployed (Railway/Render)
- [ ] Frontend deployed (Vercel)
- [ ] Demo video recorded (2 min)
- [ ] Patent abstract ready
- [ ] All team members credited

---

## 📞 Need Help?

- Check `docs/` folder for detailed guides
- Review error messages carefully
- Google specific error messages
- Check API status pages:
  - OpenAI: https://status.openai.com/
  - Vercel: https://www.vercel-status.com/

---

## 🎉 You're Ready!

Your FoodSense AI+ application should now be running.

**Next Steps**:
1. Test all features
2. Customize for your presentation
3. Practice demo script
4. Record video
5. Win hackathon! 🏆

**Good luck!**
