"""
Free Travel APIs - Easy to get, no credit card required
1. SerpAPI (Google Search) - Free 100 searches/month
   Get key: https://serpapi.com/users/signup
2. Exa API - Already configured (free 1000 searches/month)
"""
import requests
from config import Config

# Common airport codes mapping
AIRPORT_CODES = {
    "new york": "JFK", "nyc": "JFK", "los angeles": "LAX", "chicago": "ORD",
    "miami": "MIA", "san francisco": "SFO", "boston": "BOS", "seattle": "SEA",
    "london": "LHR", "paris": "CDG", "tokyo": "NRT", "dubai": "DXB",
    "singapore": "SIN", "bangkok": "BKK", "mumbai": "BOM", "delhi": "DEL",
    "bangalore": "BLR", "chennai": "MAA", "kolkata": "CCU", "hyderabad": "HYD",
    "goa": "GOI", "jaipur": "JAI", "kerala": "COK"
}


def get_airport_code(city: str) -> str:
    """Get IATA airport code for a city."""
    city_lower = city.lower().strip()
    # Check direct mapping
    if city_lower in AIRPORT_CODES:
        return AIRPORT_CODES[city_lower]
    # Check if already an airport code
    if len(city) == 3 and city.isalpha():
        return city.upper()
    # Return as-is (SerpAPI may handle it)
    return city


def search_flights_serp(origin: str, destination: str, date: str) -> list:
    """
    Search flights using SerpAPI (Google Flights results).
    Free, no credit card needed.
    """
    if not Config.SERPAPI_KEY:
        return []

    # Convert city names to airport codes
    origin_code = get_airport_code(origin)
    dest_code = get_airport_code(destination)

    try:
        url = "https://serpapi.com/search.json"
        params = {
            "engine": "google_flights",
            "departure_id": origin_code,
            "arrival_id": dest_code,
            "outbound_date": date,
            "api_key": Config.SERPAPI_KEY
        }

        resp = requests.get(url, params=params, timeout=30)

        if resp.status_code == 400:
            print(f"[SerpAPI] Bad request for {origin_code} -> {dest_code}. Using web search fallback.")
            return []

        resp.raise_for_status()
        data = resp.json()

        results = []
        for flight in data.get("flights", [])[:5]:
            results.append({
                "title": flight.get("airline", "Flight"),
                "snippet": f"${flight.get('price', 0)} - {flight.get('duration', '')}",
                "price": flight.get('price', 0),
                "airline": flight.get("airline", ""),
                "departure_time": flight.get("departure_time", ""),
                "arrival_time": flight.get("arrival_time", ""),
                "duration": flight.get("duration", ""),
                "stops": len(flight.get("segments", [])) - 1 if "segments" in flight else 0
            })
        return results

    except Exception as e:
        print(f"[SerpAPI Flight Error] {e}")
        return []


def search_hotels_serp(destination: str, check_in: str, check_out: str) -> list:
    """
    Search hotels using SerpAPI (Google Hotels results).
    """
    if not Config.SERPAPI_KEY:
        return []

    try:
        url = "https://serpapi.com/search.json"
        params = {
            "engine": "google_hotels",
            "destination": destination,
            "check_in_date": check_in,
            "check_out_date": check_out,
            "api_key": Config.SERPAPI_KEY
        }

        resp = requests.get(url, params=params, timeout=30)

        if resp.status_code == 400:
            print(f"[SerpAPI] Bad request for hotels in {destination}. Using web search fallback.")
            return []

        resp.raise_for_status()
        data = resp.json()

        results = []
        for hotel in data.get("hotels", [])[:5]:
            results.append({
                "title": hotel.get("title", "Hotel"),
                "snippet": f"{hotel.get('rating', '')} - {hotel.get('address', '')}",
                "name": hotel.get("title", "Hotel"),
                "location": hotel.get("address", ""),
                "price_per_night": hotel.get("price", 0),
                "rating": hotel.get("rating", 0),
                "amenities": hotel.get("amenities", [])
            })
        return results

    except Exception as e:
        print(f"[SerpAPI Hotel Error] {e}")
        return []


def search_restaurants_serp(destination: str) -> list:
    """
    Search restaurants using SerpAPI (Google Maps results).
    """
    if not Config.SERPAPI_KEY:
        return []

    try:
        url = "https://serpapi.com/search.json"
        params = {
            "engine": "google_maps",
            "type": "restaurant",
            "q": f"best restaurants in {destination}",
            "ll": f"@{destination}",  # Use location search
            "api_key": Config.SERPAPI_KEY
        }

        resp = requests.get(url, params=params, timeout=30)

        if resp.status_code == 400:
            print(f"[SerpAPI] Bad request for restaurants in {destination}. Using web search fallback.")
            return []

        resp.raise_for_status()
        data = resp.json()

        results = []
        for place in data.get("local_results", [])[:8]:
            results.append({
                "title": place.get("title", "Restaurant"),
                "snippet": f"{place.get('rating', '')} ({place.get('reviews', 0)} reviews)",
                "name": place.get("title", "Restaurant"),
                "location": place.get("address", ""),
                "rating": place.get("rating", 0),
                "reviews": place.get("reviews", 0),
                "type": place.get("type", "Restaurant")
            })
        return results

    except Exception as e:
        print(f"[SerpAPI Restaurant Error] {e}")
        return []


def search_attractions_serp(destination: str) -> list:
    """
    Search attractions using SerpAPI (Google Maps results).
    """
    if not Config.SERPAPI_KEY:
        return []

    try:
        url = "https://serpapi.com/search.json"
        params = {
            "engine": "google_maps",
            "type": "attraction",
            "q": f"top attractions in {destination}",
            "api_key": Config.SERPAPI_KEY
        }

        resp = requests.get(url, params=params, timeout=30)

        if resp.status_code == 400:
            print(f"[SerpAPI] Bad request for attractions in {destination}. Using web search fallback.")
            return []

        resp.raise_for_status()
        data = resp.json()

        results = []
        for place in data.get("local_results", [])[:8]:
            results.append({
                "title": place.get("title", "Attraction"),
                "snippet": f"{place.get('rating', '')} - {place.get('address', '')}",
                "name": place.get("title", ""),
                "location": place.get("address", ""),
                "rating": place.get("rating", 0)
            })
        return results

    except Exception as e:
        print(f"[SerpAPI Attraction Error] {e}")
        return []
