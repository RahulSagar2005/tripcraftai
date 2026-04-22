import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/tripcraft')
    DB_NAME = 'tripcraft'

    # LLM APIs - FREE MODELS ONLY
    # NVIDIA API (free tier, high limits) - Get key: https://build.nvidia.com/
    NVIDIA_API_KEY = os.environ.get('NVIDIA_API_KEY', '')
    # Ollama (local) - No API key needed, runs on localhost:11434
    # Hugging Face (free tier) - Get key: https://huggingface.co/settings/tokens
    HUGGINGFACE_API_KEY = os.environ.get('HUGGINGFACE_API_KEY', '')
    # OpenRouter (free models) - Get key: https://openrouter.ai/keys
    OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', '')
    # Google Gemini (free tier available) - Get key: https://aistudio.google.com/app/apikey
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY', '')

    # Travel APIs (Free tiers)
    EXA_API_KEY = os.environ.get('EXA_API_KEY', '')
    FIRECRAWL_API_KEY = os.environ.get('FIRECRAWL_API_KEY', '')

    # SerpAPI - Free 100 searches/month (easiest to get)
    SERPAPI_KEY = os.environ.get('SERPAPI_KEY', '')

    # RapidAPI (for multiple travel APIs)
    RAPIDAPI_KEY = os.environ.get('RAPIDAPI_KEY', '')

    # AviationStack - Free 500 flights/month
    AVIATIONSTACK_API_KEY = os.environ.get('AVIATIONSTACK_API_KEY', '')
