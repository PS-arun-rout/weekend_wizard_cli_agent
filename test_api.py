#!/usr/bin/env python3
"""Test script to verify API connection."""
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Get configuration
api_key = os.getenv("AI_API_TOKEN") or os.getenv("LLM_API_KEY")
base_url = os.getenv("LLM_BASE_URL")
model = os.getenv("LLM_MODEL") or "glm 4.7 reasoning"

print("=" * 60)
print("API Connection Test")
print("=" * 60)
print(f"Base URL: {base_url}")
print(f"Model: {model}")
print(f"API Key: {'*' * 20}{api_key[-10:] if api_key else 'NOT SET'}")
print("=" * 60)

# Check if required variables are set
if not api_key:
    print("❌ ERROR: AI_API_TOKEN or LLM_API_KEY is not set")
    exit(1)

if not base_url:
    print("❌ ERROR: LLM_BASE_URL is not set")
    exit(1)

# Create client and test connection
try:
    print("\n🔄 Testing API connection...")
    client = OpenAI(api_key=api_key, base_url=base_url)
    
    # Make a simple test call
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'API connection successful!' in exactly those words."}
        ],
        temperature=0.2,
        max_tokens=50
    )
    
    # Extract and display result
    result = response.choices[0].message.content
    print(f"✅ API connection successful!")
    print(f"📝 Response: {result}")
    print(f"📊 Usage: {response.usage}")
    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}")
    print(f"   {str(e)}")
    print("\n" + "=" * 60)
    print("❌ API connection failed!")
    print("=" * 60)
    exit(1)