# 🌍 TripCraft AI

**Your Journey, Perfectly Crafted with Intelligence**

An AI-powered travel planner that generates personalised itineraries with flights, hotels, dining, day-by-day plans, destination guides, and a full budget breakdown — built on a multi-agent architecture and free-tier LLM APIs.

---

## ✨ Features

- **7-step planning wizard** — destination, group, budget, vibes, stay, pace, personal touch
- **6 AI agents working in parallel** — flights, hotels, dining, itinerary, destination guide, budget
- **Real-time web search** — SerpAPI (Google) for flights/hotels/restaurants, DuckDuckGo as fallback
- **Day-by-day itinerary** — morning, afternoon, evening with specific times and notes
- **Destination guide** — attractions, transport, culture, safety, emergency contacts
- **Dining recommendations** — filtered by dietary needs and travel style
- **Budget analysis** — full cost breakdown, day-wise estimates, savings tips
- **User accounts** — sign up, sign in, saved trip plans
- **Background processing** — trip generation runs in a worker thread with live progress

---

## 🗂️ Project Structure

```
tripcraft_ai/
├── app.py                     # Flask app, routes, auth, health check
├── config.py                  # Configuration (API keys, DB)
├── models.py                  # MongoDB models (User, Trip)
├── requirements.txt
├── Procfile                   # Railway / Heroku start command
├── railway.json               # Railway deploy config
├── render.yaml                # Render deploy config (alternative)
├── runtime.txt                # Python version for Railway
├── .python-version            # pyenv / nixpacks version
│
├── agents/
│   ├── orchestrator.py        # Coordinates all 6 agents
│   ├── flight_agent.py
│   ├── hotel_agent.py
│   ├── food_agent.py
│   ├── planner_agent.py       # Day-by-day itinerary + destination guide
│   └── budget_agent.py
│
├── utils/
│   ├── llm_client.py          # OpenRouter / NVIDIA / Ollama / HF (with fallback chain)
│   ├── exa_search.py          # SerpAPI + DuckDuckGo fallback
│   ├── travel_api.py          # SerpAPI flight/hotel/restaurant/attraction search
│   └── firecrawl_scraper.py
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── auth.html
│   ├── plan.html
│   ├── processing.html
│   ├── result.html
│   └── my_plans.html
│
└── static/
    ├── css/main.css
    └── js/main.js, plan.js
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM | OpenRouter (free models) → NVIDIA API (fallback) → Ollama (optional local) |
| Travel search | SerpAPI (Google) + DuckDuckGo fallback |
| Backend | Flask 3 + gunicorn |
| Database | MongoDB (local or Atlas) |
| Auth | Flask-Login + Flask-Bcrypt |
| Frontend | Jinja2 + vanilla JS + custom CSS |

---

## 🚀 Quick Start (Local)

```bash
# 1. Clone and set up Python
git clone <your-repo>
cd tripcraft_ai
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env              # then edit .env (see "API Keys" below)

# 4. Run
python app.py
```

App will be available at **http://localhost:5000**

---

## 🔑 API Keys

The app works with a **single LLM key** (OpenRouter recommended) plus a MongoDB connection. Everything else is optional.

### Required

| Key | Purpose | Where to get it | Free? |
|-----|---------|-----------------|-------|
| `MONGODB_URI` | User + trip storage | Local: `mongodb://localhost:27017/tripcraft` <br> Atlas: https://www.mongodb.com/cloud/atlas (free M0 cluster) | ✅ |
| `OPENROUTER_API_KEY` | Primary LLM | https://openrouter.ai/keys | ✅ |
| `SECRET_KEY` | Flask session signing | `python -c "import secrets; print(secrets.token_hex(32))"` | — |

### Recommended (for real flight/hotel/restaurant data)

| Key | Purpose | Where to get it | Free? |
|-----|---------|-----------------|-------|
| `SERPAPI_KEY` | Real Google Flights / Hotels / Maps data | https://serpapi.com/users/signup | ✅ 100 searches/month |
| `NVIDIA_API_KEY` | Secondary LLM (auto-fallback) | https://build.nvidia.com/ | ✅ ~1000 req/day |

### Optional

| Key | Purpose | Where to get it | Free? |
|-----|---------|-----------------|-------|
| `HUGGINGFACE_API_KEY` | Extra LLM fallback | https://huggingface.co/settings/tokens | ✅ |
| `EXA_API_KEY` | Extra web search | https://exa.ai | ✅ 1000/month |
| `FIRECRAWL_API_KEY` | Web scraping | https://firecrawl.dev | ✅ 500/month |
| `AVIATIONSTACK_API_KEY` | Flight data | https://aviationstack.com | ✅ 500/month |
| Ollama (no key) | 100% local LLM | https://ollama.ai → `ollama pull llama3.2` | ✅ Unlimited |

### ⚠️ Important: do NOT use the previous Gemini key

The Gemini key that was in the project (`AIzaSyA7TfcIv5LlkEfz8u-kIPWRamYvcEPezco`) was **permanently banned by Google** — they returned:

```
HTTP 403 - "Your API key was reported as leaked. Please use another API key."
```

That is not a bug in the code; it is a Google-side policy decision on that key. If you need Gemini, generate a **brand-new** key at https://aistudio.google.com/app/apikey and wire it back in. Until then, the app routes around Gemini entirely and uses OpenRouter as the primary LLM.

---

## 🌐 Deploy to Railway

This repo is pre-configured for Railway — no extra setup needed beyond linking the repo and adding env vars.

### One-time setup

1. Push the repo to GitHub.
2. Go to https://railway.app → **New Project → Deploy from GitHub repo** → pick this repo.
3. Railway auto-detects Python, installs from `requirements.txt`, and starts gunicorn via the `Procfile`.

### Set environment variables (in the Railway dashboard)

```
MONGODB_URI = mongodb+srv://user:pass@cluster.mongodb.net/tripcraft
SECRET_KEY  = <a long random string>
OPENROUTER_API_KEY = sk-or-v1-...
NVIDIA_API_KEY     = nvapi-...        (optional, recommended)
SERPAPI_KEY        = ...              (optional, recommended for real data)
```

### Verify the deploy

Once deployed, hit `https://<your-app>.up.railway.app/health` — it should return:

```json
{"status": "ok"}
```

### Notes

- `railway.json` is the canonical config; the `Procfile` is a fallback.
- `runtime.txt` pins Python 3.11.9.
- The `Procfile` runs `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`. The `$PORT` env var is provided by Railway.
- The app also works on Render — `render.yaml` is provided as an alternative.

---

## 🤖 How the AI Agents Work

```
User submits 7-step form
        │
        ▼
   Orchestrator (agents/orchestrator.py)
        │
        ├── ✈️ Flight Agent   → SerpAPI / web search → LLM
        ├── 🏨 Hotel Agent    → SerpAPI / web search → LLM
        ├── 🍽️ Food Agent     → SerpAPI / web search → LLM
        ├── 🗓️ Planner Agent  → all agent data + LLM  → day-by-day itinerary
        ├── 🗺️ Guide Agent    → web search + LLM      → destination guide
        └── 💰 Budget Agent   → all cost data + LLM   → budget breakdown
        │
        ▼
   Complete trip plan saved to MongoDB
        │
        ▼
   Result page (5 tabs: Itinerary, Guide, Flights, Dining, Budget)
```

The orchestrator runs the agents sequentially (with a 3-second delay between them to avoid rate limits) and stores the merged result in the `trips` collection.

---

## 🧪 Verifying Locally

After updating your `.env`, run a quick health check:

```bash
# Quick LLM sanity test
python test_llm.py

# Full API + DB test
python test_setup.py

# Start the app
python app.py
```

`test_llm.py` confirms at least one LLM provider responds. `test_setup.py` checks the keys in `.env` and pings NVIDIA, OpenRouter, and SerpAPI directly.

---

## 🛠️ Customisation

- **Swap the LLM** — edit `utils/llm_client.py`. The fallback chain is:
  1. Ollama (if installed locally)
  2. OpenRouter
  3. NVIDIA
  4. Hugging Face
- **Add a new agent** — create `agents/my_agent.py`, expose `run_my_agent(trip_data)`, then call it from `agents/orchestrator.py`.
- **Change the wizard** — `templates/plan.html` and `static/js/plan.js`.

---

## 🐛 Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| "All LLM providers unavailable" | No key in `.env`, or all keys invalid | Set `OPENROUTER_API_KEY` (minimum). Run `python test_llm.py`. |
| Trip stuck on "processing" | One of the agents threw; check Flask logs | See the traceback in the terminal where `app.py` is running. |
| `[SerpAPI] Bad request` for flights | Missing `return_date` for round-trip | Fixed: the flight agent now passes `return_date`. If you see the message for an unusual route, SerpAPI just doesn't have data for that origin/destination pair — the agent falls back to web search. |
| `[SerpAPI] Bad request: Missing query "q" parameter` | Outdated `search_*_serp` signature | Fixed: hotels/restaurants/attractions all send `q` now. |
| `[SerpAPI] "X" is not included in the list` | Old code passed a `type` filter to the `google_maps` engine | Fixed: `type` is no longer sent; we bias by `q` and `ll` instead. |
| `[OpenRouter] Error 402` | Free credits exhausted for that model | The client now auto-cycles through 4 verified working models (`meta-llama/llama-3-8b-instruct`, `meta-llama/llama-3.1-8b-instruct`, `meta-llama/llama-3.3-70b-instruct`, `qwen/qwen-2.5-7b-instruct`). If all 4 return 402, your OpenRouter account is out of free credits. Either top up at https://openrouter.ai/credits or let it fall through to NVIDIA (already wired in). |
| MongoDB connection timeout | Wrong URI or Atlas IP not whitelisted | Use Atlas Network Access → "Allow access from anywhere" (0.0.0.0/0) for testing, then restrict. |
| `Gemini 403 leaked` | Google's permanent ban on the old key | Use OpenRouter / NVIDIA instead. Get a fresh Gemini key only if you really need it. |
| App crashes on Railway | Missing env var | Check the Railway **Variables** tab — `MONGODB_URI` and `SECRET_KEY` are required. |

---

## 📄 License

MIT — Build freely, travel wonderfully. 🌍
