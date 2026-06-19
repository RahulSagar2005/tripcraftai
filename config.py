import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    # Railway's MongoDB plugin injects MONGO_URL / MONGO_DB; fall back to MONGODB_URI.
    MONGODB_URI = (
        os.environ.get('MONGO_URL')
        or os.environ.get('MONGODB_URI')
        or 'mongodb://localhost:27017/tripcraft'
    )
    DB_NAME = os.environ.get('MONGO_DB') or os.environ.get('DB_NAME') or 'tripcraft'

    # ── LLM API keys (FREE TIER ONLY) ──────────────────────────────────────
    # Primary cloud (free models, confirmed working)
    # Get a key: https://openrouter.ai/keys
    OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', '')

    # Secondary cloud (free tier, has known-working model list)
    # Get a key: https://build.nvidia.com/
    NVIDIA_API_KEY = os.environ.get('NVIDIA_API_KEY', '')

    # Optional: Hugging Face free-tier fallback
    # Get a key: https://huggingface.co/settings/tokens
    HUGGINGFACE_API_KEY = os.environ.get('HUGGINGFACE_API_KEY', '')

    # Optional local LLM (no key, runs on localhost:11434) - install from
    # https://ollama.ai and run `ollama pull llama3.2`

    # Gemini is intentionally NOT used. The previous key was banned by
    # Google (403 - reported as leaked). The slot is kept commented for
    # reference and a future brand-new key.
    # GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY', '')

    # ── Travel APIs ────────────────────────────────────────────────────────
    # SerpAPI - free 100 searches/month (Google Flights, Hotels, Maps)
    # Get a key: https://serpapi.com/users/signup (no credit card)
    SERPAPI_KEY = os.environ.get('SERPAPI_KEY', '')

    # Exa (web search) - free 1000 searches/month
    EXA_API_KEY = os.environ.get('EXA_API_KEY', '')

    # Firecrawl (web scraping) - free 500 pages/month
    FIRECRAWL_API_KEY = os.environ.get('FIRECRAWL_API_KEY', '')

    # RapidAPI (multi-API hub, optional)
    RAPIDAPI_KEY = os.environ.get('RAPIDAPI_KEY', '')

    # AviationStack (flight data) - free 500 flights/month
    AVIATIONSTACK_API_KEY = os.environ.get('AVIATIONSTACK_API_KEY', '')
