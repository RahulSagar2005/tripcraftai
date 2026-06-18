import os
import json
import requests
import time
from config import Config

# Ollama Local LLM Configuration (Primary - Completely Free)
OLLAMA_BASE = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2"

# NVIDIA API Configuration (Secondary Cloud - Free Tier, High Limits)
NVIDIA_API_KEY = Config.NVIDIA_API_KEY
NVIDIA_API_BASE = "https://integrate.api.nvidia.com/v1"
# Verified working model IDs on integrate.api.nvidia.com
# Note: NVIDIA uses 'meta/' (single slash) for Meta models, not 'meta-llama/'
# Order matters: faster 8B-class models first, big 70B models last because
# they can hit timeouts on long prompts (planner agent, etc.).
NVIDIA_MODELS = [
    "meta/llama-3.1-8b-instruct",
    "mistralai/mistral-large-2-instruct",
    "google/gemma-3-12b-it",
    "meta/llama-3.1-70b-instruct",
    "meta/llama-3.3-70b-instruct",
]

# NOTE: Google Gemini is no longer used.
# The previous key was rejected by Google (403 - "API key was reported as leaked")
# and the free Gemini path is no longer wired up. Keep GOOGLE_API_KEY in .env
# for reference but don't call Gemini until a brand-new key is provided.

# Hugging Face Inference API (Free Tier - Fallback)
HF_API_BASE = "https://api-inference.huggingface.co/models"
HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.3"

# OpenRouter API Configuration (Free Models Only - Last Fallback)
OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"


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


def _call_nvidia(prompt: str, system_prompt: str = "", max_tokens: int = 4096) -> str:
    """Call NVIDIA API (free tier - secondary cloud option).

    Tries each model in NVIDIA_MODELS in order; returns the first successful
    response. Returns None if all fail or the key is missing.
    """
    if not NVIDIA_API_KEY:
        return None

    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    url = f"{NVIDIA_API_BASE}/chat/completions"

    for model in NVIDIA_MODELS:
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.7,
            "stream": False
        }
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=120)

            if resp.status_code == 401:
                print("[NVIDIA] Authentication failed - check API key at https://build.nvidia.com/")
                return None
            if resp.status_code == 404:
                print(f"[NVIDIA] Model '{model}' not available, trying next...")
                continue
            if resp.status_code == 429:
                print(f"[NVIDIA] Rate limited on '{model}', trying next...")
                continue
            if resp.status_code >= 400:
                print(f"[NVIDIA] {model} -> {resp.status_code}: {resp.text[:200]}")
                continue

            data = resp.json()
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]

        except requests.exceptions.RequestException as e:
            print(f"[NVIDIA] Network error on '{model}': {e}")
            continue
        except Exception as e:
            print(f"[NVIDIA] Unexpected error on '{model}': {type(e).__name__}: {e}")
            continue

    print("[NVIDIA] All models failed")
    return None


def _call_openrouter(prompt: str, system_prompt: str = "", max_tokens: int = 4000) -> str:
    """Call OpenRouter API with FREE models only"""
    api_key = Config.OPENROUTER_API_KEY
    # Check for valid OpenRouter key format (v1 or v2)
    if not api_key or not api_key.startswith("sk-or-") or len(api_key) < 15:
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

    # Use only models verified to have live endpoints on OpenRouter
    # Note: many "free" :free-suffixed models have been retired; the non-free
    # slugs below all worked at the time of testing.
    openrouter_models = [
        "meta-llama/llama-3-8b-instruct",
        "meta-llama/llama-3.1-8b-instruct",
        "meta-llama/llama-3.3-70b-instruct",
        "qwen/qwen-2.5-7b-instruct",
    ]

    # Cycle through each model on retry
    model_index = [0]

    def next_model():
        idx = model_index[0]
        model_index[0] = (idx + 1) % len(openrouter_models)
        return openrouter_models[model_index[0]]

    payload = {
        "model": openrouter_models[0],
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.7
    }

    max_retries = 3
    base_delay = 5

    for attempt in range(max_retries):
        try:
            resp = requests.post(f"{OPENROUTER_API_BASE}/chat/completions", headers=headers, json=payload, timeout=180)

            if resp.status_code == 401:
                print("[OpenRouter] Authentication failed - check API key")
                return None
            elif resp.status_code == 402:
                # Payment required - usually means free credits exhausted for
                # this model. Try the next one in the list.
                next_m = next_model()
                payload["model"] = next_m
                print(f"[OpenRouter] 402 on previous model, switching to: {next_m}")
                time.sleep(base_delay)
                continue
            elif resp.status_code == 404:
                # Model has no endpoints. Skip to the next one.
                next_m = next_model()
                payload["model"] = next_m
                print(f"[OpenRouter] Model unavailable, switching to: {next_m}")
                time.sleep(base_delay)
                continue
            elif resp.status_code == 429:
                print("[OpenRouter] Rate limited on free tier")
                return None
            elif resp.status_code in (502, 503):
                wait_time = base_delay * (attempt + 1)
                print(f"[OpenRouter] Server error. Waiting {wait_time}s...")
                time.sleep(wait_time)
                continue

            if resp.status_code >= 400:
                print(f"[OpenRouter] Error {resp.status_code}: {resp.text[:200]}")
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
    """DISABLED: Google Gemini integration is no longer used.

    The previous key was reported as leaked by Google and is permanently
    banned (HTTP 403 - PERMISSION_DENIED). The function is kept as a stub
    so any code that still imports it doesn't crash, but it always returns
    None until a brand-new key from https://aistudio.google.com/app/apikey
    is wired up and tested.
    """
    return None


def call_llm(prompt: str, system_prompt: str = "", max_tokens: int = 4096) -> str:
    """
    Call LLM with automatic fallback chain (FREE MODELS ONLY):

    1. Ollama local LLM (primary - completely free, no API key needed, optional)
    2. OpenRouter free models (primary cloud - confirmed working)
    3. NVIDIA API (secondary cloud - free tier, verified models)
    4. Hugging Face Inference API (free tier, optional)
    5. Gemini - DISABLED (key was reported as leaked by Google)
    """
    # Try Ollama first (local, completely free, only if user has it installed)
    result = _call_ollama(prompt, system_prompt, max_tokens)
    if result:
        return result

    # OpenRouter is the reliable primary cloud (free models, confirmed working)
    if Config.OPENROUTER_API_KEY:
        result = _call_openrouter(prompt, system_prompt, max_tokens)
        if result:
            return result

    # NVIDIA as the secondary cloud (also free, has known-working model list)
    if NVIDIA_API_KEY:
        print("[LLM] Falling back to NVIDIA...")
        result = _call_nvidia(prompt, system_prompt, max_tokens)
        if result:
            return result

    # Hugging Face as a last resort (free tier)
    hf_key = os.environ.get("HUGGINGFACE_API_KEY", "")
    if hf_key:
        print("[LLM] Falling back to Hugging Face...")
        result = _call_huggingface(prompt, system_prompt, max_tokens)
        if result:
            return result

    return (
        "Error: All LLM providers unavailable. "
        "Install Ollama (https://ollama.ai) and run 'ollama pull llama3.2', "
        "or set OPENROUTER_API_KEY / NVIDIA_API_KEY in your environment."
    )


def _fix_json_expressions(text: str) -> str:
    """Fix common JSON issues like uncomputed expressions (e.g., '100 * 4' -> '400')."""
    import re

    # Fix multiplication expressions like "100 * 4"
    def eval_mult(match):
        try:
            expr = match.group(0)
            # Only allow simple arithmetic
            result = eval(expr.replace(" ", ""))
            return str(result)
        except:
            return match.group(0)

    # Pattern for simple arithmetic in JSON values
    text = re.sub(r'(?<=[:\s,])\s*\d+\s*[\*\+\-\/]\s*\d+\s*(?=[,\}\]])', eval_mult, text)

    return text


def call_llm_json(prompt: str, system_prompt: str = "", max_tokens: int = 4000) -> dict:
    json_system = (system_prompt or "") + "\nYou MUST respond with valid JSON only. No markdown, no code fences, no arithmetic expressions. Just raw JSON with computed numbers."

    raw = call_llm(prompt, json_system, max_tokens)

    if not raw or raw.startswith("Error:"):
        return {"error": "No response from LLM", "raw_error": raw}

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

    # Fix common issues like uncomputed expressions
    raw = _fix_json_expressions(raw)

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"[JSON Parse Error] {e}")
        # Try to extract JSON from the response
        import re
        json_match = re.search(r'\{[\s\S]*\}', raw)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError as e2:
                print(f"[JSON Parse Error 2] {e2}")
                # Last resort: try to fix common issues
                fixed = json_match.group()
                # Remove trailing commas
                fixed = re.sub(r',\s*}', '}', fixed)
                fixed = re.sub(r',\s*]', ']', fixed)
                # Fix missing quotes around keys
                fixed = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z_0-9]*)\s*:', r'\1"\2":', fixed)
                # Fix single quotes to double quotes
                fixed = fixed.replace("'", '"')
                try:
                    return json.loads(fixed)
                except Exception as e3:
                    print(f"[JSON Parse Error 3] {e3}")
                    pass
        return {"error": str(e), "raw": raw[:1000]}