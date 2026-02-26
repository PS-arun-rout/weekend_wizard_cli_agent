#!/usr/bin/env python3
"""Test script to verify Weather API connection."""
import requests
import json
import urllib3

# Suppress SSL warnings for testing only
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

print("=" * 60)
print("Weather API Connection Test")
print("=" * 60)

# Test coordinates (New York City)
latitude = 40.7128
longitude = -74.0060

print(f"\n📍 Testing with coordinates:")
print(f"   Latitude: {latitude}")
print(f"   Longitude: {longitude}")

# Open-Meteo API endpoint
url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": latitude,
    "longitude": longitude,
    "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
}

print(f"\n🔄 Testing API connection...")
print(f"   URL: {url}")
print(f"   Params: {params}")

try:
    # Make the API call with verify=False to bypass SSL issues
    response = requests.get(url, params=params, timeout=10, verify=False)
    response.raise_for_status()
    
    # Parse JSON response
    data = response.json()
    
    print(f"\n✅ API connection successful!")
    print(f"   Status Code: {response.status_code}")
    print(f"\n📊 Weather Data:")
    print(json.dumps(data, indent=2))
    
    # Extract current weather
    if "current" in data:
        current = data["current"]
        print(f"\n🌡️  Current Weather:")
        print(f"   Temperature: {current.get('temperature_2m', 'N/A')}°C")
        print(f"   Humidity: {current.get('relative_humidity_2m', 'N/A')}%")
        print(f"   Apparent Temperature: {current.get('apparent_temperature', 'N/A')}°C")
        print(f"   Wind Speed: {current.get('wind_speed_10m', 'N/A')} km/h")
        print(f"   Weather Code: {current.get('weather_code', 'N/A')}")
    
    print("\n" + "=" * 60)
    print("✅ Weather API test passed!")
    print("=" * 60)
    
except requests.exceptions.Timeout:
    print(f"\n❌ ERROR: Request timed out after 10 seconds")
    print("\n" + "=" * 60)
    print("❌ Weather API test failed!")
    print("=" * 60)
    exit(1)
    
except requests.exceptions.HTTPError as e:
    print(f"\n❌ ERROR: HTTP error occurred")
    print(f"   Status Code: {e.response.status_code}")
    print(f"   Response: {e.response.text}")
    print("\n" + "=" * 60)
    print("❌ Weather API test failed!")
    print("=" * 60)
    exit(1)
    
except requests.exceptions.RequestException as e:
    print(f"\n❌ ERROR: {type(e).__name__}")
    print(f"   {str(e)}")
    print("\n" + "=" * 60)
    print("❌ Weather API test failed!")
    print("=" * 60)
    exit(1)
    
except json.JSONDecodeError as e:
    print(f"\n❌ ERROR: Failed to parse JSON response")
    print(f"   {str(e)}")
    print(f"   Response text: {response.text[:200]}")
    print("\n" + "=" * 60)
    print("❌ Weather API test failed!")
    print("=" * 60)
    exit(1)