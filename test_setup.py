"""
Test script to verify all API connections are working.
Run: python test_setup.py
"""
import os
from dotenv import load_dotenv
load_dotenv()

print("=" * 50)
print("TRIPCRAFT AI - API SETUP TEST")
print("=" * 50)

# Test 1: Check .env loading
print("\n[1] Checking .env file...")
from config import Config

checks = {
    "NVIDIA_API_KEY": Config.NVIDIA_API_KEY,
    "GOOGLE_API_KEY": Config.GOOGLE_API_KEY,
    "OPENROUTER_API_KEY": Config.OPENROUTER_API_KEY,
    "SERPAPI_KEY": Config.SERPAPI_KEY,
}

all_ok = True
for name, value in checks.items():
    if value and len(value) > 10:
        print(f"  [OK] {name}: {value[:10]}...{value[-5:]}")
    else:
        print(f"  [MISSING] {name}")
        all_ok = False

# Test 2: Test NVIDIA API
print("\n[2] Testing NVIDIA API (Primary Cloud)...")
from utils.llm_client import _call_nvidia
result = _call_nvidia("Say 'Hello, NVIDIA API works!' in exactly 5 words.")
if result:
    print(f"  [OK] NVIDIA Response: {result[:50]}...")
else:
    print(f"  [FAIL] NVIDIA API - check your API key at https://build.nvidia.com/")

# Test 3: Test Gemini API
print("\n[3] Testing Gemini API (Secondary Cloud)...")
from utils.llm_client import _call_gemini
result = _call_gemini("Say 'Hello, Gemini works!' in exactly 5 words.")
if result:
    print(f"  [OK] Gemini Response: {result[:50]}...")
else:
    print(f"  [FAIL] Gemini API - check key at https://aistudio.google.com/app/apikey")

# Test 4: Test OpenRouter
print("\n[4] Testing OpenRouter API (Free Models)...")
from utils.llm_client import _call_openrouter
result = _call_openrouter("Say hello in exactly 5 words.")
if result:
    print(f"  [OK] OpenRouter Response: {result[:50]}...")
else:
    print(f"  [FAIL] OpenRouter API - check key at https://openrouter.ai/keys")

# Test 5: Test SerpAPI (Travel Search)
print("\n[5] Testing SerpAPI (Travel Search)...")
from utils.travel_api import search_attractions_serp
results = search_attractions_serp("Goa")
if results:
    print(f"  [OK] SerpAPI found {len(results)} attractions in Goa")
    print(f"       Top result: {results[0].get('title', 'N/A')}")
else:
    print(f"  [FAIL] SerpAPI - check key at https://serpapi.com/users/signup")

# Test 6: Test JSON parsing
print("\n[6] Testing JSON parsing with arithmetic...")
from utils.llm_client import call_llm_json
test_result = call_llm_json(
    "Return ONLY this JSON with computed values: {'total': 100 * 4, 'name': 'test'}"
)
if "error" not in test_result:
    print(f"  [OK] JSON parsed: {test_result}")
else:
    print(f"  [WARN] JSON parse issue: {test_result.get('error', 'Unknown')}")

print("\n" + "=" * 50)
print("SETUP TEST COMPLETE")
print("=" * 50)

if all_ok:
    print("\nAll API keys configured! Run: python app.py")
else:
    print("\nSome API keys missing. Update .env file.")
    print("\nGet FREE API keys:")
    print("  - NVIDIA: https://build.nvidia.com/ (recommended)")
    print("  - Gemini: https://aistudio.google.com/app/apikey")
    print("  - SerpAPI: https://serpapi.com/users/signup")
    print("  - OpenRouter: https://openrouter.ai/keys")
