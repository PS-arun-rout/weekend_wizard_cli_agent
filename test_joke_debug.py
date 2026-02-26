#!/usr/bin/env python3
"""Debug script for joke API."""
import urllib3
import requests

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://v2.jokeapi.dev/joke/Any"
params = {"safe-mode": "", "type": "single"}

print(f"Testing Joke API...")
print(f"URL: {url}")
print(f"Params: {params}")

try:
    resp = requests.get(url, params=params, timeout=10, verify=False)
    print(f"Status Code: {resp.status_code}")
    print(f"Response: {resp.text}")
    
    data = resp.json()
    print(f"\nParsed JSON:")
    print(f"  error: {data.get('error')}")
    print(f"  type: {data.get('type')}")
    print(f"  joke: {data.get('joke')}")
    print(f"  setup: {data.get('setup')}")
    print(f"  delivery: {data.get('delivery')}")
    
except Exception as e:
    print(f"Error: {e}")