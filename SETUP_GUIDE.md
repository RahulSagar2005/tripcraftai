# TripCraft AI - FREE API Setup Guide

## Quick Summary

Your current API keys are **configured but invalid/expired**. Follow this guide to get **100% FREE** working keys.

---

## Step 1: Get NVIDIA API Key (Primary LLM - Recommended)

**Why**: Free, high limits (1000+ requests/day), high-quality models

1. Go to: https://build.nvidia.com/
2. Click **"Sign In"** (use Google/GitHub account - free)
3. Go to: https://build.nvidia.com/meta/llama-3.1-70b-instruct
4. Click **"Get API Key"**
5. Copy the key (starts with `nvapi-`)
6. Update your `.env` file:
   ```
   NVIDIA_API_KEY=nvapi-YOUR_NEW_KEY_HERE
   ```

**Alternative models available**:
- `mistralai/mistral-large-2-instruct`
- `google/gemma-7b`
- `meta/llama-3.1-70b-instruct`

---

## Step 2: Get Google Gemini API Key (Backup LLM)

**Why**: Free tier, very reliable, good for travel content

1. Go to: https://aistudio.google.com/app/apikey
2. Click **"Create API Key"**
3. Select your Google project (or create new)
4. Copy the key (starts with `AIzaSy`)
5. Update your `.env` file:
   ```
   GOOGLE_API_KEY=AIzaSyYOUR_NEW_KEY_HERE
   ```

**Note**: The current key `AIzaSyA7TfcIv5LlkEfz8u-kIPWRamYvcEPezco` is returning 404 - it may be expired or from a different project.

---

## Step 3: Get SerpAPI Key (Travel Search - CRITICAL)

**Why**: Real flight/hotel/restaurant data from Google

1. Go to: https://serpapi.com/users/signup
2. Sign up (no credit card needed)
3. Verify your email
4. Go to: https://serpapi.com/manage-api-key
5. Copy your API key
6. Update your `.env` file:
   ```
   SERPAPI_KEY=YOUR_NEW_KEY_HERE
   ```

**Free limit**: 100 searches/month (enough for ~25 trip plans)

**Note**: Your current key `7c413a691325dd2d94102c5c8521803df717b836c23f80e9cc79ddec0dc9e0b` is **INVALID**.

---

## Step 4: Get OpenRouter API Key (Last Resort LLM)

**Why**: Access to multiple free models

1. Go to: https://openrouter.ai/keys
2. Create account (free)
3. Generate new API key
4. Update your `.env` file:
   ```
   OPENROUTER_API_KEY=sk-or-v1-YOUR_NEW_KEY_HERE
   ```

**Free models available**:
- `google/gemma-2-9b-it:free`
- `meta-llama/llama-3-8b-instruct:free`
- `mistralai/mistral-7b-instruct:free`

---

## After Getting Keys

1. **Update `.env` file** with all new keys
2. **Restart your Flask app**:
   ```powershell
   # Stop current app (Ctrl+C)
   python app.py
   ```

3. **Test the setup**:
   ```powershell
   python test_setup.py
   ```

---

## Expected Test Results (All Working)

```
[OK] NVIDIA_API_KEY: nvapi-...
[OK] GOOGLE_API_KEY: AIzaSy...
[OK] OPENROUTER_API_KEY: sk-or-...
[OK] SERPAPI_KEY: ...

[OK] NVIDIA Response: Hello, NVIDIA API works!...
[OK] Gemini Response: Hello, Gemini works!...
[OK] OpenRouter Response: Hello, OpenRouter works!...
[OK] SerpAPI found 8 attractions in Goa
```

---

## Troubleshooting

### "All LLM providers unavailable"
- Check NVIDIA API key at https://build.nvidia.com/
- Ensure key starts with `nvapi-`
- Try Gemini as backup

### SerpAPI still failing
- The free 100 searches/month resets monthly
- If exhausted, wait for next month or create new account
- Web search fallback (DuckDuckGo) will still work

### Ollama (Optional - Completely Free Local LLM)
If you want a completely free local option (no API keys needed):

1. Install Ollama: https://ollama.ai/download
2. Run: `ollama pull llama3.2`
3. Ollama will auto-start on `localhost:11434`
4. No API key needed - works offline!

---

## Summary: Minimum Required Keys

For **basic free operation**, you need:

| Service | Purpose | Free Limit | Required |
|---------|---------|------------|----------|
| **NVIDIA API** | Main LLM | 1000+/day | YES |
| **SerpAPI** | Flight/Hotel search | 100/month | YES |
| Gemini | Backup LLM | 60/minute | Optional |
| OpenRouter | Last resort LLM | Varies | Optional |

---

## Quick Start (Minimal Setup)

If you want the **fastest setup**:

1. Get **NVIDIA API key** only: https://build.nvidia.com/
2. Get **SerpAPI key** only: https://serpapi.com/users/signup
3. Add to `.env`:
   ```
   NVIDIA_API_KEY=nvapi-...
   SERPAPI_KEY=...
   ```
4. Run: `python app.py`

The app will work with just these two keys!

---

## Current Issues in Your Setup

| Component | Status | Issue |
|-----------|--------|-------|
| NVIDIA API | Configured | Key invalid/expired |
| Gemini API | Configured | Key from wrong project or expired |
| OpenRouter | Configured | Key invalid |
| SerpAPI | Configured | **INVALID** - wrong key format |
| Ollama | Not running | Not installed |

**Action needed**: Get fresh keys for NVIDIA and SerpAPI (minimum).
