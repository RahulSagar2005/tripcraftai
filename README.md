# 🌍 TripCraft AI

**Your Journey, Perfectly Crafted with Intelligence**

An end-to-end AI-powered travel planning platform that generates fully personalized itineraries using a multi-agent AI system, real-time flight/hotel search, and a beautiful 7-step planning wizard.

---

## 📸 Features

- **7-Step Planning Wizard** — Destination, group, budget, vibes, stay, pace, personal touch
- **Multi-Agent AI System** — 6 specialized agents running in parallel
- **Real Flight Options** — Live search via Exa API
- **Hotel Recommendations** — Matched to your style and budget
- **Day-by-Day Itinerary** — Morning, afternoon, evening with times
- **Destination Guide** — Attractions, transport, culture, safety
- **Dining Recommendations** — Filtered by dietary needs
- **Budget Analysis** — Full cost breakdown + savings tips
- **User Authentication** — Sign up, sign in, saved plans
- **Processing Animation** — Live agent status during generation

---

## 🗂️ Project Structure

```
tripcraft_ai/
├── app.py                     # Flask app, routes, auth
├── config.py                  # Configuration (API keys, DB)
├── models.py                  # SQLAlchemy models (User, Trip)
├── requirements.txt
├── .env.example
│
├── agents/
│   ├── __init__.py
│   ├── orchestrator.py        # Coordinates all agents
│   ├── flight_agent.py        # Searches real flights
│   ├── hotel_agent.py         # Finds accommodations
│   ├── food_agent.py          # Restaurant recommendations
│   ├── planner_agent.py       # Day-by-day itinerary + guide
│   └── budget_agent.py        # Cost breakdown & optimization
│
├── utils/
│   ├── __init__.py
│   ├── llm_client.py          # OpenRouter/Gemini API wrapper
│   ├── exa_search.py          # Exa search API (real-time data)
│   └── firecrawl_scraper.py   # Firecrawl web scraping
│
├── templates/
│   ├── base.html              # Navbar, layout
│   ├── index.html             # Homepage
│   ├── auth.html              # Sign in / Sign up
│   ├── plan.html              # 7-step planning form
│   ├── processing.html        # AI agent progress page
│   ├── result.html            # Full trip result (5 tabs)
│   └── my_plans.html          # Saved trips dashboard
│
└── static/
    ├── css/
    │   └── main.css           # Full styling
    └── js/
        ├── main.js            # Global interactions
        └── plan.js            # Form wizard logic + submission
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **AI Engine** | Gemini 2.0 Flash via OpenRouter |
| **Search** | Exa API (real-time web search) |
| **Scraping** | Firecrawl (web content extraction) |
| **Backend** | Flask (Python) |
| **Database** | SQLite via SQLAlchemy |
| **Auth** | Flask-Login + Bcrypt |
| **Frontend** | Jinja2 + Vanilla JS + Custom CSS |
| **Fonts** | Syne (headings) + DM Sans (body) |

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone <your-repo>
cd tripcraft_ai

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
cp .env.example .env
```

Edit `.env` with your keys:

```env
OPENROUTER_API_KEY=your_openrouter_key   # https://openrouter.ai
EXA_API_KEY=your_exa_key                 # https://exa.ai
FIRECRAWL_API_KEY=your_firecrawl_key     # https://firecrawl.dev
SECRET_KEY=a-long-random-secret-string
```

### 3. Run

```bash
python app.py
```

Open **http://localhost:5000**

---

## 🔑 Getting API Keys

| API | Where to Get | Free Tier |
|-----|-------------|-----------|
| OpenRouter | https://openrouter.ai/keys | Yes — Gemini 2.0 Flash is cheap |
| Exa | https://exa.ai | Yes — 1000 searches/month free |
| Firecrawl | https://firecrawl.dev | Yes — 500 pages/month free |

---

## 🤖 AI Agent Workflow

```
User submits 7-step form
        │
        ▼
   Orchestrator
        │
   ┌────┴──────────────────────────┐
   │                               │
✈️ Flight Agent          🏨 Hotel Agent
(Exa search → LLM)      (Exa search → LLM)
        │                          │
   ┌────┴──────────────────────────┘
   │
🍽️ Food Agent
(Exa search → LLM)
        │
   ┌────┴──────────────────────────┐
   │                               │
🗓️ Planner Agent         🗺️ Guide Agent
(Exa + all agent data → LLM)   (Exa → LLM)
        │
   ┌────┴────────┐
   │
💰 Budget Agent
(all cost data → LLM analysis)
        │
        ▼
  Complete Trip Plan
  Stored in SQLite
        │
        ▼
  Result Page (5 tabs)
```

Each agent:
1. **Searches** for real-time data via Exa API
2. **Passes** real search results + user preferences to Gemini 2.0 Flash
3. **Returns** structured JSON parsed by the orchestrator

---

## 📋 Result Page Tabs

| Tab | Content |
|-----|---------|
| **Itinerary** | Day-by-day plan (morning/afternoon/evening) with times |
| **Destination Guide** | Attractions, transport, culture, safety, emergency contacts |
| **Flights** | Outbound + return options with prices, recommended choice |
| **Dining** | Restaurant recommendations filtered by dietary preferences |
| **Budget** | Full breakdown, day-wise estimates, savings tips |

---

## 🛠️ Customization

**Change the LLM model** — Edit `config.py`:
```python
GEMINI_MODEL = "google/gemini-2.0-flash-001"  # or any OpenRouter model
```

**Add more agents** — Create a file in `agents/`, implement `run_X_agent(trip_data)`, and add it to `orchestrator.py`.

**Change database** — Update `SQLALCHEMY_DATABASE_URI` in `config.py`:
```python
SQLALCHEMY_DATABASE_URI = 'postgresql://user:pass@localhost/tripcraft'
```

---

## 📝 Notes

- Trip generation runs in a **background thread** — users see live progress
- All results are stored in SQLite and viewable from **My Plans**
- If API keys are missing/invalid, agents return graceful error messages
- The form auto-prefills the user's name from their account

---

## 🐛 Troubleshooting

**Trip stuck on "processing"** — Check terminal for agent errors. Most common: invalid API key.

**LLM returns bad JSON** — The `call_llm_json` utility strips markdown fences and retries parsing.

**Exa returns no results** — Check your `EXA_API_KEY` and quota at exa.ai dashboard.

---

## 📄 License

MIT — Build freely, travel wonderfully. 🌍
