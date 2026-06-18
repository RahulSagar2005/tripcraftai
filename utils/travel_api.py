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
    "new delhi": "DEL", "bangalore": "BLR", "chennai": "MAA", "kolkata": "CCU",
    "hyderabad": "HYD", "goa": "GOI", "jaipur": "JAI", "kerala": "COK",
    "agra": "AGR", "lucknow": "LKO", "varanasi": "VNS", "amritsar": "ATQ",
    "srinagar": "SXR", "leh": "IXL", "manali": "KUU", "shimla": "SLV",
    "udaipur": "UDR", "jodhpur": "JDH", "ahmedabad": "AMD", "pune": "PNQ",
    "nagpur": "NAG", "cochin": "COK", "trivandrum": "TRV", "visakhapatnam": "VTZ",
    "patna": "PAT", "ranchi": "IXR", "bhubaneswar": "BBI", "guwahati": "GAU",
    "shillong": "SHL", "gangtok": "PYG", "darjeeling": "IXB", "puri": "BBI",
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


def search_flights_serp(origin: str, destination: str, date: str, return_date: str = None) -> list:
    """
    Search flights using SerpAPI (Google Flights results).
    Free, no credit card needed.

    If return_date is provided, requests a round-trip search; otherwise a
    one-way search. SerpAPI's google_flights engine returns 400 if `type`
    is the default round-trip but no return_date is supplied, so we set
    type=1 (round trip) only when both dates are available.
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
        if return_date:
            params["type"] = "1"          # round trip
            params["return_date"] = return_date
        else:
            params["type"] = "2"          # one way

        resp = requests.get(url, params=params, timeout=30)

        if resp.status_code == 401:
            print("[SerpAPI] Authentication failed - check API key at https://serpapi.com/manage-api-key")
            return []
        if resp.status_code == 400:
            # Surface the actual error from SerpAPI for easier debugging
            try:
                err = resp.json().get("error", "unknown")
            except Exception:
                err = resp.text[:120]
            print(f"[SerpAPI] Bad request for {origin_code} -> {dest_code}: {err}. Using web search fallback.")
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

    SerpAPI's google_hotels engine requires a `q` (search query) parameter;
    the `destination` field alone returns 400. We pass the city name as `q`
    which works for any destination.
    """
    if not Config.SERPAPI_KEY:
        return []

    try:
        url = "https://serpapi.com/search.json"
        params = {
            "engine": "google_hotels",
            "q": f"hotels in {destination}",
            "check_in_date": check_in,
            "check_out_date": check_out,
            "api_key": Config.SERPAPI_KEY
        }

        resp = requests.get(url, params=params, timeout=30)

        if resp.status_code == 400:
            try:
                err = resp.json().get("error", "unknown")
            except Exception:
                err = resp.text[:120]
            print(f"[SerpAPI] Bad request for hotels in {destination}: {err}. Using web search fallback.")
            return []

        resp.raise_for_status()
        data = resp.json()

        # SerpAPI returns the list under "properties" (not "hotels") in the
        # current schema. Fall back to "hotels" for older responses.
        hotel_list = data.get("properties") or data.get("hotels") or []
        results = []
        for hotel in hotel_list[:5]:
            results.append({
                "title": hotel.get("title") or hotel.get("name", "Hotel"),
                "snippet": f"{hotel.get('rating', '')} - {hotel.get('address', '')}",
                "name": hotel.get("title") or hotel.get("name", "Hotel"),
                "location": hotel.get("address", ""),
                "price_per_night": hotel.get("price", 0) or hotel.get("rate_per_night", {}).get("extracted_lowest", 0),
                "rating": hotel.get("rating", 0),
                "amenities": hotel.get("amenities", [])
            })
        return results

    except Exception as e:
        print(f"[SerpAPI Hotel Error] {e}")
        return []


def _geocode_location(destination: str) -> tuple:
    """
    Get lat/lng coordinates for a destination using SerpAPI or simple fallback.
    Returns (lat, lng) or None if not found.
    """
    # Common India cities coordinates (fallback)
    india_coords = {
        "amritsar": (31.6340, 74.8723),
        "chandigarh": (30.7333, 76.7794),
        "ludhiana": (30.9010, 75.8573),
        "patiala": (30.3398, 76.3869),
        "patiala": (30.3398, 76.3869),
        "jalandhar": (31.3260, 75.5762),
        "punjab": (30.7333, 76.7794),  # Default to Chandigarh (Punjab capital)
        "delhi": (28.6139, 77.2090),
        "mumbai": (19.0760, 72.8777),
        "bangalore": (12.9716, 77.5946),
        "chennai": (13.0827, 80.2707),
        "kolkata": (22.5726, 88.3639),
        "goa": (15.2993, 74.1240),
        "jaipur": (26.9124, 75.7873),
        "kerala": (10.8505, 76.2711)
    }

    dest_lower = destination.lower().strip()
    if dest_lower in india_coords:
        return india_coords[dest_lower]

    # Try SerpAPI geocoding
    if Config.SERPAPI_KEY:
        try:
            url = "https://serpapi.com/search.json"
            params = {
                "engine": "google_maps",
                "q": destination,
                "api_key": Config.SERPAPI_KEY
            }
            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if "place_results" in data:
                    gps = data["place_results"].get("gps_coordinates", {})
                    return (gps.get("latitude"), gps.get("longitude"))
        except:
            pass

    return None


def search_restaurants_serp(destination: str) -> list:
    """
    Search restaurants using SerpAPI (Google Maps results).

    google_maps engine does NOT accept a `type` parameter (it returns
    "is not included in the list"). We use the `q` query to scope the
    search and `ll` to bias by coordinates when available.
    """
    if not Config.SERPAPI_KEY:
        return []

    coords = _geocode_location(destination)

    try:
        url = "https://serpapi.com/search.json"
        params = {
            "engine": "google_maps",
            "q": f"best restaurants in {destination}",
            "api_key": Config.SERPAPI_KEY
        }

        # Use coordinates if available to bias the local pack
        if coords:
            params["ll"] = f"@{coords[0]},{coords[1]},13z"

        resp = requests.get(url, params=params, timeout=30)

        if resp.status_code == 400:
            try:
                err = resp.json().get("error", "unknown")
            except Exception:
                err = resp.text[:120]
            print(f"[SerpAPI] Bad request for restaurants in {destination}: {err}. Using web search fallback.")
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

    google_maps engine does NOT accept a `type` parameter. We bias by
    coordinates and let the `q` query phrase the request.
    """
    if not Config.SERPAPI_KEY:
        return []

    coords = _geocode_location(destination)

    try:
        url = "https://serpapi.com/search.json"

        params = {
            "engine": "google_maps",
            "q": f"top tourist attractions in {destination}",
            "api_key": Config.SERPAPI_KEY
        }

        # Use coordinates if available to bias the local pack
        if coords:
            params["ll"] = f"@{coords[0]},{coords[1]},12z"

        resp = requests.get(url, params=params, timeout=30)

        if resp.status_code == 400:
            try:
                err = resp.json().get("error", "unknown")
            except Exception:
                err = resp.text[:120]
            print(f"[SerpAPI] Bad request for attractions in {destination}: {err}. Using web search fallback.")
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
