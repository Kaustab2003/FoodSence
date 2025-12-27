# Multi-Language Feature Usage Guide

## How to Use FoodSense AI+ in Your Local Language

### Step 1: Select Your Language

1. Open FoodSense AI+ (http://localhost:3000)
2. Look for the **language selector** in the top-right corner (🌐 icon)
3. Click on it to open the language menu
4. Select your preferred language from the list:
   - English
   - हिन्दी (Hindi)
   - বাংলা (Bengali)
   - தமிழ் (Tamil)
   - తెలుగు (Telugu)
   - मराठी (Marathi)
   - ગુજરાતી (Gujarati)
   - ಕನ್ನಡ (Kannada)
   - മലയാളം (Malayalam)
   - ਪੰਜਾਬੀ (Punjabi)

### Step 2: Enter Product Information

Now you can use **any of these methods** in your selected language:

#### Method 1: Voice Input 🎤
- Click the **microphone button**
- Speak the product name or ingredients **in your language**
- The system will recognize and transcribe in your selected language
- Example (Hindi): "चीनी, नमक, गेहूं का आटा"

#### Method 2: Camera Capture 📸
- Click **"📸 Capture ingredients photo"**
- Allow camera permission
- Point camera at ingredient label **in your language**
- Click capture
- OCR will read text in your selected language script

#### Method 3: File Upload 📁
- Click **"📁 Upload ingredients photo"**
- Select a photo of ingredients from your device
- OCR will extract text in your selected language

#### Method 4: Manual Typing ⌨️
- Type product name in your language
- Type ingredients in your language (comma-separated)

### Step 3: Get Analysis

1. Click **"✨ Analyze Food"** button
2. Wait for AI analysis
3. Results will be displayed **in your selected language**:
   - Summary in your language
   - Health insights in your language
   - Follow-up questions in your language

### Features That Support Your Language:

✅ **Voice Recognition** - Speak in your language
✅ **OCR (Photo/Upload)** - Read text in your script
✅ **AI Analysis** - Get results in your language
✅ **Product Names** - Write names in your language
✅ **Ingredients** - List ingredients in your language

### Example Workflow (Hindi):

1. **Select Language**: Click 🌐 → Choose "हिन्दी"
2. **Voice Input**: Click 🎤 → Say "नमक, चीनी, मैदा"
3. **Or Camera**: Click 📸 → Capture Hindi label
4. **Analyze**: Click "✨ Analyze Food"
5. **Results**: See analysis in Hindi

### Storage:

- Your language preference is **saved automatically**
- Next time you open the app, your language is **remembered**
- Stored in browser's localStorage

### Switching Languages:

- You can **change language anytime**
- Click language selector → Choose new language
- All future inputs/outputs use new language
- Previous data stays in original language

### Best Practices:

1. **For OCR**: Take clear, well-lit photos of ingredient labels
2. **For Voice**: Speak clearly in quiet environment
3. **For Typing**: Use native keyboard for your language
4. **Internet Required**: Translation needs active connection

### Technical Details:

- **Voice Recognition**: Uses Web Speech API with language-specific codes
- **OCR**: Uses Tesseract.js with trained data for Indian scripts
- **Translation**: Uses Gemini AI for accurate translations
- **Supported Scripts**: All major Indian language scripts

### Troubleshooting:

**Voice not working?**
- Check browser supports your language (Chrome/Edge recommended)
- Grant microphone permission
- Ensure "हिन्दी" shows in language selector

**OCR not reading correctly?**
- Ensure good lighting
- Keep text straight (not angled)
- Try higher resolution photo
- Verify correct language selected

**Results in English despite language selection?**
- Check backend is running (uvicorn should be active)
- Ensure internet connection for AI translation
- Try refreshing page

### Language Codes Reference:

| Language | Code | Voice Code | OCR Code |
|----------|------|------------|----------|
| English | en | en-IN | eng |
| Hindi | hi | hi-IN | hin |
| Bengali | bn | bn-IN | ben |
| Tamil | ta | ta-IN | tam |
| Telugu | te | te-IN | tel |
| Marathi | mr | mr-IN | mar |
| Gujarati | gu | gu-IN | guj |
| Kannada | kn | kn-IN | kan |
| Malayalam | ml | ml-IN | mal |
| Punjabi | pa | pa-IN | pan |

---

**Enjoy using FoodSense AI+ in your native language! 🎉**
