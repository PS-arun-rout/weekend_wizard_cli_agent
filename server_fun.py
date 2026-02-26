import html
import urllib3
from typing import Any, Dict

import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weekend_wizard")

TIMEOUT = 10

# Suppress SSL warnings for development
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def _safe_get_json(url: str, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
    try:
        # Use verify=False to bypass SSL certificate issues on Windows
        # Note: In production, you should fix the SSL certificate chain
        resp = requests.get(url, params=params, timeout=TIMEOUT, verify=False)
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:  # noqa: BLE001 - return error to caller
        return {"error": str(exc)}


@mcp.tool()
def get_weather(latitude: float, longitude: float) -> Dict[str, Any]:
    """Get current weather from Open-Meteo."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
    }
    return _safe_get_json(url, params=params)


@mcp.tool()
def book_recs(topic: str, limit: int = 5) -> Dict[str, Any]:
    """Search Open Library for book recommendations."""
    url = "https://openlibrary.org/search.json"
    params = {"q": topic, "limit": limit}
    return _safe_get_json(url, params=params)


@mcp.tool()
def random_joke() -> Dict[str, Any]:
    """Fetch a safe, single-line joke from JokeAPI."""
    url = "https://v2.jokeapi.dev/joke/Any"
    params = {"safe-mode": "", "type": "single"}
    return _safe_get_json(url, params=params)


@mcp.tool()
def random_dog() -> Dict[str, Any]:
    """Fetch a random dog image URL from Dog CEO."""
    url = "https://dog.ceo/api/breeds/image/random"
    return _safe_get_json(url)


@mcp.tool()
def trivia() -> Dict[str, Any]:
    """Fetch a trivia question from Open Trivia DB."""
    url = "https://opentdb.com/api.php"
    params = {"amount": 1, "type": "multiple"}
    data = _safe_get_json(url, params=params)
    if "error" in data:
        return data
    try:
        results = data.get("results", [])
        if not results:
            return {"error": "No trivia results."}
        q = results[0]
        q["question"] = html.unescape(q.get("question", ""))
        q["correct_answer"] = html.unescape(q.get("correct_answer", ""))
        q["incorrect_answers"] = [html.unescape(a) for a in q.get("incorrect_answers", [])]
        return q
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)}


if __name__ == "__main__":
    mcp.run()
