# Installing Tesseract OCR (Optional Fallback)

Tesseract OCR provides a local fallback when Gemini API quota is exceeded.

## Windows Installation

### Option 1: Using Chocolatey (Recommended)
```powershell
choco install tesseract
```

### Option 2: Manual Download
1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install the `.exe` file
3. Add to PATH: `C:\Program Files\Tesseract-OCR`

## Verify Installation
```bash
tesseract --version
```

## Alternative Solutions

If you don't want to install Tesseract, you can:

1. **Wait for Gemini quota reset** (resets daily)
2. **Use a different Google API key**
3. **Add HuggingFace API key** to `.env`:
   ```
   HUGGINGFACE_API_KEY=your_key_here
   ```

## Current Status

- ✅ Gemini API: Configured (Quota: 20 requests/day)
- ⚠️ Tesseract OCR: Not installed
- ❌ HuggingFace API: Not configured

The app will show a user-friendly error message when quota is exceeded.
