#!/usr/bin/env python3
"""
Test script to verify LLM setup for TripCraft AI
Run this to check which LLM providers are working.
"""

import sys
sys.path.insert(0, '.')

from utils.llm_client import call_llm, call_llm_json

def test_llm():
    print("=" * 50)
    print("TripCraft AI - LLM Provider Test")
    print("=" * 50)

    # Test 1: Simple text generation
    print("\n[Test 1] Testing basic LLM call...")
    result = call_llm("Say 'Hello from TripCraft!' in exactly 5 words.")
    print(f"Result: {result}")

    if result and "Error" not in result:
        print("[SUCCESS] LLM is working!")
    else:
        print("[FAILED] All LLM providers failed")
        print("\nSolutions:")
        print("1. Install Ollama: https://ollama.ai")
        print("   Then run: ollama pull llama3.2")
        print("2. Or get a free Gemini API key: https://aistudio.google.com/app/apikey")
        print("3. Or get a free OpenRouter key: https://openrouter.ai/keys")
        return False

    # Test 2: JSON generation
    print("\n[Test 2] Testing JSON generation...")
    result = call_llm_json('Return a JSON object with a "greeting" key and "world" as value.')
    print(f"Result: {result}")

    if isinstance(result, dict) and not result.get("error"):
        print("[SUCCESS] JSON generation working!")
        return True
    else:
        print("[PARTIAL] Text generation works, but JSON parsing may need improvement")
        return True

if __name__ == "__main__":
    test_llm()
