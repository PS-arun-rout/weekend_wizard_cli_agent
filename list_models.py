#!/usr/bin/env python3
"""List available models from the API."""
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Get configuration
api_key = os.getenv("AI_API_TOKEN") or os.getenv("LLM_API_KEY")
base_url = os.getenv("LLM_BASE_URL")

print("=" * 60)
print("Available Models")
print("=" * 60)
print(f"Base URL: {base_url}")
print("=" * 60)

try:
    client = OpenAI(api_key=api_key, base_url=base_url)
    models = client.models.list()
    
    print(f"\n✅ Found {len(models.data)} model(s):\n")
    for model in models.data:
        print(f"  • {model.id}")
    
    print("\n" + "=" * 60)
    
except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}")
    print(f"   {str(e)}")
    print("\n" + "=" * 60)