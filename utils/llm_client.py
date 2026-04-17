import os
import json
import requests
import time
from config import Config

# Ollama Local LLM Configuration (Primary - Completely Free)
OLLAMA_BASE = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2"

# Google Gemini API Configuration (Primary Cloud - Free Tier)
GEMINI_API_KEY = Config.GOOGLE_API_KEY
GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"
GEMINI_MODEL = "gemini-1.5-flash"

# Hugging Face Inference API (Free Tier - Fallback)
HF_API_BASE = "https://api-inference.huggingface.co/models"
HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.3"

# OpenRouter API Configuration (Free Models Only - Last Fallback)
OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"
OPENROUTER_MODEL = "google/gemma-2-9b-it:free"


def _call_ollama(prompt: str, system_prompt: str = "", max_tokens: int = 4096) -> str:
    """Call local Ollama LLM (primary method - completely free)"""
    headers = {"Content-Type": "application/json"}

    system_instruction = system_prompt if system_prompt else "You are a helpful travel assistant."

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "options": {
            "temperature": 0.7,
            "top_p": 0.9,
            "num_predict": max_tokens
        }
    }

    try:
        resp = requests.post(
            f"{OLLAMA_BASE}/api/chat",
            headers=headers,
            json=payload,
            timeout=120
        )

        if resp.status_code >= 400:
            print(f"[Ollama] Error {resp.status_code} - is Ollama running?")
            return None

        data = resp.json()
        content = data.get("message", {}).get("content", "")

        if content:
            return content

        print("[Ollama] No valid response")
        return None

    except requests.exceptions.ConnectionError:
        print("[Ollama] Connection refused - is Ollama running on localhost:11434?")
        return None
    except Exception as e:
        print(f"[Ollama] Error: {type(e).__name__}: {e}")
        return None


def _call_huggingface(prompt: str, system_prompt: str = "", max_tokens: int = 4096) -> str:
    """Call Hugging Face Inference API (free tier)"""
    api_key = os.environ.get("HUGGINGFACE_API_KEY", "")
    if not api_key:
        return None

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Format for instruction-tuned model
    formatted_prompt = f"<s>[INST] {system_prompt or 'You are a helpful travel assistant.'}\n\n{prompt} [/INST]"

    payload = {
        "inputs": formatted_prompt,
        "parameters": {
            "max_new_tokens": max_tokens,
            "temperature": 0.7,
            "top_p": 0.9,
            "return_full_text": False
        }
    }

    try:
        resp = requests.post(
            f"{HF_API_BASE}/{HF_MODEL}",
            headers=headers,
            json=payload,
            timeout=120
        )

        if resp.status_code == 401:
            print("[HuggingFace] Authentication failed - check API key")
            return None
        elif resp.status_code == 503:
            print("[HuggingFace] Model loading - try again in a moment")
            return None
        elif resp.status_code >= 400:
            print(f"[HuggingFace] Error {resp.status_code}")
            return None

        data = resp.json()
        if isinstance(data, list) and len(data) > 0:
            return data[0].get("generated_text", "")

        print("[HuggingFace] No valid response")
        return None

    except Exception as e:
        print(f"[HuggingFace] Error: {type(e).__name__}: {e}")
        return None


def _call_openrouter(prompt: str, system_prompt: str = "", max_tokens: int = 4000) -> str:
    """Call OpenRouter API with FREE models only"""
    api_key = Config.OPENROUTER_API_KEY
    # Check for valid OpenRouter key format
    if not api_key or not (api_key.startswith("sk-or-") or api_key.startswith("sk-or-v1-")) or len(api_key) < 15:
        return None

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "TripCraft AI"
    }

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    # Use only FREE models available on OpenRouter
    free_models = [
        "google/gemma-2-9b-it:free",
        "meta-llama/llama-3-8b-instruct:free",
        "mistralai/mistral-7b-instruct:free",
        "google/gemma-7b-it:free"
    ]

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.7
    }

    max_retries = 2
    base_delay = 5

    for attempt in range(max_retries):
        try:
            resp = requests.post(f"{OPENROUTER_API_BASE}/chat/completions", headers=headers, json=payload, timeout=180)

            if resp.status_code == 401:
                print("[OpenRouter] Authentication failed - check API key")
                return None
            elif resp.status_code == 404:
                # Try next free model in list
                if attempt < len(free_models) - 1:
                    payload["model"] = free_models[attempt + 1]
                    print(f"[OpenRouter] Trying next free model: {payload['model']}")
                    continue
                return None
            elif resp.status_code == 429:
                print("[OpenRouter] Rate limited on free tier")
                return None
            elif resp.status_code in (502, 503):
                wait_time = base_delay * (attempt + 1)
                print(f"[OpenRouter] Server error. Waiting {wait_time}s...")
                time.sleep(wait_time)
                continue

            if resp.status_code >= 400:
                print(f"[OpenRouter] Error {resp.status_code}")
                return None

            data = resp.json()
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]
            return None

        except Exception as e:
            print(f"[OpenRouter] Error: {type(e).__name__}: {e}")
            if attempt < max_retries - 1:
                time.sleep(base_delay)
                continue
            return None

    return None


def _call_gemini(prompt: str, system_prompt: str = "", max_tokens: int = 8192) -> str:
    """Call Google Gemini API (primary cloud fallback - free tier)"""
    if not GEMINI_API_KEY:
        return None

    headers = {"Content-Type": "application/json"}
    system_instruction = system_prompt if system_prompt else "You are a helpful travel assistant."

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "systemInstruction": {"parts": [{"text": system_instruction}]},
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": 0.7
        }
    }

    try:
        resp = requests.post(
            f"{GEMINI_API_BASE}/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}",
            headers=headers,
            json=payload,
            timeout=120
        )

        if resp.status_code == 400:
            print(f"[Gemini] Bad request - {resp.json()}")
            return None
        elif resp.status_code == 429:
            print(f"[Gemini] Rate limited (free tier limit reached)")
            return None
        elif resp.status_code >= 500:
            print(f"[Gemini] Server error {resp.status_code}")
            return None

        resp.raise_for_status()
        data = resp.json()

        if "candidates" in data and len(data["candidates"]) > 0:
            content = data["candidates"][0].get("content", {})
            if "parts" in content and len(content["parts"]) > 0:
                return content["parts"][0].get("text", "")

        print("[Gemini] No valid response in candidates")
        return None

    except Exception as e:
        print(f"[Gemini] Error: {type(e).__name__}: {e}")
        return None


def call_llm(prompt: str, system_prompt: str = "", max_tokens: int = 4096) -> str:
    """
    Call LLM with automatic fallback chain (FREE MODELS ONLY):
    1. Ollama local LLM (primary - completely free, no API key needed)
    2. Hugging Face Inference API (free tier, requires HF API key)
    3. OpenRouter API (free models only)
    4. Google Gemini API (last fallback)
    """
    # Try Ollama first (local, completely free)
    result = _call_ollama(prompt, system_prompt, max_tokens)
    if result:
        return result

    # Try Hugging Face (free tier)
    hf_key = os.environ.get("HUGGINGFACE_API_KEY", "")
    if hf_key:
        print("[LLM] Falling back to Hugging Face...")
        result = _call_huggingface(prompt, system_prompt, max_tokens)
        if result:
            return result

    # Try OpenRouter (free models)
    if Config.OPENROUTER_API_KEY:
        print("[LLM] Falling back to OpenRouter (free models)...")
        result = _call_openrouter(prompt, system_prompt, max_tokens)
        if result:
            return result

    # Try Gemini last
    if GEMINI_API_KEY:
        print("[LLM] Falling back to Gemini...")
        result = _call_gemini(prompt, system_prompt, max_tokens)
        if result:
            return result

    return "Error: All LLM providers unavailable. Please install Ollama (ollama.ai) and run 'ollama pull llama3.2', or set HUGGINGFACE_API_KEY or OPENROUTER_API_KEY environment variables."


def call_llm_json(prompt: str, system_prompt: str = "", max_tokens: int = 4000) -> dict:
    json_system = (system_prompt or "") + "\nYou MUST respond with valid JSON only. No markdown, no code fences. Just raw JSON."

    raw = call_llm(prompt, json_system, max_tokens)

    raw = raw.strip()

    # Remove markdown code fences if present
    if raw.startswith("```"):
        lines = raw.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        raw = "\n".join(lines)
    elif "```json" in raw:
        raw = raw.replace("```json", "").replace("```", "")

    raw = raw.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"[JSON Parse Error] {e}\nRaw: {raw[:500]}")
        # Try to extract JSON from the response
        import re
        json_match = re.search(r'\{[\s\S]*\}', raw)
        if json_match:
            try:
                return json.loads(json_match.group())
            except:
                pass
        return {"error": str(e), "raw": raw[:1000]}