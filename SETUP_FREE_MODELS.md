# TripCraft AI - Free Models Setup Guide

This guide shows you how to run TripCraft AI using **completely free** LLM models.

## Quick Start (Recommended)

### Option 1: Ollama (Best - Completely Free, No API Key)

1. **Install Ollama**: Download from https://ollama.ai

2. **Pull the model** (run in terminal):
   ```bash
   ollama pull llama3.2
   ```

3. **Start Ollama** (usually auto-starts when installed)

4. **Run TripCraft**:
   ```bash
   python app.py
   ```

That's it! No API keys needed. Ollama runs locally on your machine.

---

### Option 2: Hugging Face (Free Tier)

1. **Get API Key**: https://huggingface.co/settings/tokens

2. **Create `.env` file**:
   ```bash
   HUGGINGFACE_API_KEY=your_key_here
   ```

3. **Run TripCraft**:
   ```bash
   python app.py
   ```

---

### Option 3: OpenRouter (Free Models)

1. **Get API Key**: https://openrouter.ai/keys

2. **Create `.env` file**:
   ```bash
   OPENROUTER_API_KEY=sk-or-your-key-here
   ```

3. **Run TripCraft**:
   ```bash
   python app.py
   ```

OpenRouter provides free access to models like:
- Google Gemma 2 9B
- Meta Llama 3 8B
- Mistral 7B

---

### Option 4: Google Gemini (Free Tier)

1. **Get API Key**: https://aistudio.google.com/app/apikey

2. **Create `.env` file**:
   ```bash
   GOOGLE_API_KEY=your_key_here
   ```

3. **Run TripCraft**:
   ```bash
   python app.py
   ```

---

## Travel APIs (Optional but Recommended)

### SerpAPI - Free 100 searches/month

Provides real data from Google Flights, Google Hotels, and Google Maps.

1. **Get Key**: https://serpapi.com/users/signup (no credit card needed)

2. **Add to `.env`**:
   ```bash
   SERPAPI_KEY=your_serpapi_key_here
   ```

Without SerpAPI, the app falls back to web search which provides simulated data.

---

## Full `.env` File Example

```env
# Flask
SECRET_KEY=dev-secret-key-change-in-production

# MongoDB
MONGODB_URI=mongodb://localhost:27017/tripcraft

# LLM (pick one - Ollama needs no key)
HUGGINGFACE_API_KEY=hf_xxx
OPENROUTER_API_KEY=sk-or-xxx
GOOGLE_API_KEY=xxx

# Travel APIs
SERPAPI_KEY=xxx
```

---

## Troubleshooting

### "All LLM providers unavailable"

1. Make sure Ollama is running: `ollama list`
2. If not installed, download from https://ollama.ai
3. Or set up HuggingFace/OpenRouter/Gemini API keys

### SerpAPI "Bad request" errors

- Some city pairs don't have direct flight data
- The app automatically falls back to web search
- This is normal behavior

### MongoDB connection errors

- Make sure MongoDB is running locally, or
- Use MongoDB Atlas (free tier): https://www.mongodb.com/cloud/atlas

---

## Model Comparison

| Provider | Speed | Quality | Limits |
|----------|-------|---------|--------|
| Ollama (local) | Fast | Good | Unlimited |
| HuggingFace | Medium | Good | ~10k tokens/day |
| OpenRouter | Fast | Good | Varies by model |
| Gemini | Fast | Excellent | 1500 requests/day |

---

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install Ollama (optional but recommended)
# Download from: https://ollama.ai
ollama pull llama3.2

# Create .env file
cp .env.example .env

# Run the app
python app.py
```

Visit http://localhost:5000 to start planning your trip!
