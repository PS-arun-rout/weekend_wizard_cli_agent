#!/usr/bin/env python3
"""Test script to verify all API connections."""
import html
import urllib3
from typing import Any, Dict

import requests

# Suppress SSL warnings for development
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TIMEOUT = 10


def _safe_get_json(url: str, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
    try:
        resp = requests.get(url, params=params, timeout=TIMEOUT, verify=False)
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:
        return {"error": str(exc)}


def test_weather():
    """Test weather API."""
    print("\n" + "=" * 60)
    print("Testing Weather API (Open-Meteo)")
    print("=" * 60)
    
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 40.7128,
        "longitude": -74.0060,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
    }
    
    result = _safe_get_json(url, params=params)
    
    if "error" in result:
        print(f"❌ FAILED: {result['error']}")
        return False
    
    if "current" in result:
        current = result["current"]
        print(f"✅ SUCCESS")
        print(f"   Temperature: {current.get('temperature_2m', 'N/A')}°C")
        print(f"   Humidity: {current.get('relative_humidity_2m', 'N/A')}%")
        print(f"   Apparent Temperature: {current.get('apparent_temperature', 'N/A')}°C")
        print(f"   Wind Speed: {current.get('wind_speed_10m', 'N/A')} km/h")
        return True
    
    print(f"❌ FAILED: Unexpected response format")
    return False


def test_books():
    """Test books API."""
    print("\n" + "=" * 60)
    print("Testing Books API (Open Library)")
    print("=" * 60)
    
    url = "https://openlibrary.org/search.json"
    params = {"q": "python", "limit": 3}
    
    result = _safe_get_json(url, params=params)
    
    if "error" in result:
        print(f"❌ FAILED: {result['error']}")
        return False
    
    if "docs" in result and result["docs"]:
        print(f"✅ SUCCESS")
        print(f"   Found {len(result['docs'])} books")
        for i, book in enumerate(result["docs"][:2], 1):
            title = book.get("title", "N/A")
            author = book.get("author_name", ["N/A"])[0] if book.get("author_name") else "N/A"
            print(f"   {i}. {title} by {author}")
        return True
    
    print(f"❌ FAILED: No books found")
    return False


def test_joke():
    """Test joke API."""
    print("\n" + "=" * 60)
    print("Testing Joke API (JokeAPI)")
    print("=" * 60)
    
    url = "https://v2.jokeapi.dev/joke/Any"
    params = {"safe-mode": "", "type": "single"}
    
    result = _safe_get_json(url, params=params)
    
    # Check if error is True (not just if the key exists)
    if result.get("error") is True:
        print(f"❌ FAILED: API returned error")
        return False
    
    if "joke" in result:
        print(f"✅ SUCCESS")
        print(f"   Joke: {result['joke'][:100]}...")
        return True
    
    print(f"❌ FAILED: No joke found")
    return False


def test_dog():
    """Test dog API."""
    print("\n" + "=" * 60)
    print("Testing Dog API (Dog CEO)")
    print("=" * 60)
    
    url = "https://dog.ceo/api/breeds/image/random"
    
    result = _safe_get_json(url)
    
    if "error" in result:
        print(f"❌ FAILED: {result['error']}")
        return False
    
    if "message" in result:
        print(f"✅ SUCCESS")
        print(f"   Image URL: {result['message'][:60]}...")
        return True
    
    print(f"❌ FAILED: No image found")
    return False


def test_trivia():
    """Test trivia API."""
    print("\n" + "=" * 60)
    print("Testing Trivia API (Open Trivia DB)")
    print("=" * 60)
    
    url = "https://opentdb.com/api.php"
    params = {"amount": 1, "type": "multiple"}
    
    data = _safe_get_json(url, params=params)
    
    if "error" in data:
        print(f"❌ FAILED: {data['error']}")
        return False
    
    try:
        results = data.get("results", [])
        if not results:
            print(f"❌ FAILED: No trivia results")
            return False
        
        q = results[0]
        q["question"] = html.unescape(q.get("question", ""))
        q["correct_answer"] = html.unescape(q.get("correct_answer", ""))
        
        print(f"✅ SUCCESS")
        print(f"   Question: {q['question'][:80]}...")
        print(f"   Correct Answer: {q['correct_answer']}")
        return True
    except Exception as exc:
        print(f"❌ FAILED: {str(exc)}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("API Connection Test Suite")
    print("=" * 60)
    
    results = {
        "Weather": test_weather(),
        "Books": test_books(),
        "Joke": test_joke(),
        "Dog": test_dog(),
        "Trivia": test_trivia(),
    }
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for api, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{api:20} {status}")
    
    total = len(results)
    passed = sum(results.values())
    
    print("=" * 60)
    print(f"Total: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("✅ All API connections are working!")
        exit(0)
    else:
        print("❌ Some API connections failed!")
        exit(1)