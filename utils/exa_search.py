import requests
from config import Config


def exa_search(query: str, num_results: int = 5, include_contents: bool = True) -> list:
    """
    Search the web using SerpAPI (free 100 searches/month) or Google web search fallback.
    Returns list of result dicts with title, url, snippet/content.
    """
    # Try SerpAPI first (free, no credit card needed)
    if Config.SERPAPI_KEY:
        try:
            url = "https://serpapi.com/search.json"
            params = {
                "engine": "google",
                "q": query,
                "num": num_results,
                "api_key": Config.SERPAPI_KEY
            }
            resp = requests.get(url, params=params, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                results = []
                for r in data.get("organic_results", [])[:num_results]:
                    results.append({
                        "title": r.get("title", ""),
                        "url": r.get("link", ""),
                        "snippet": r.get("snippet", "")[:800]
                    })
                if results:
                    return results
        except Exception as e:
            print(f"[SerpAPI Search Error] {e}")

    # Fallback to DuckDuckGo HTML scraping (completely free, no API key)
    return _duckduckgo_search(query, num_results)


def _duckduckgo_search(query: str, num_results: int = 5) -> list:
    """
    Fallback web search using DuckDuckGo HTML interface (free, no API key needed).
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9"
    }
    url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"

    try:
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code != 200:
            print(f"[DuckDuckGo] Status {resp.status_code}")
            return []

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text, 'html.parser')
        results = []

        for result in soup.select('.result')[:num_results]:
            title_elem = result.select_one('.result__title')
            snippet_elem = result.select_one('.result__snippet')
            url_elem = result.select_one('.result__url')

            if title_elem and snippet_elem:
                results.append({
                    "title": title_elem.get_text(strip=True),
                    "url": url_elem.get_text(strip=True) if url_elem else "",
                    "snippet": snippet_elem.get_text(strip=True)[:800]
                })

        if results:
            print(f"[DuckDuckGo] Found {len(results)} results")
        return results

    except ImportError:
        print("[DuckDuckGo] BeautifulSoup not installed. Install: pip install beautifulsoup4")
        return []
    except Exception as e:
        print(f"[DuckDuckGo Search Error] {e}")
        return []


def search_flights(origin: str, destination: str, date: str, return_date: str = None) -> list:
    """
    Search flights - tries SerpAPI first (real Google Flights data), then web search.

    Args:
        origin:        IATA code or city name for departure
        destination:   IATA code or city name for arrival
        date:          outbound date (YYYY-MM-DD)
        return_date:   return date (YYYY-MM-DD) for round trips, optional
    """
    from utils.travel_api import search_flights_serp

    # Try SerpAPI first (real flight data from Google Flights)
    serp_results = search_flights_serp(origin, destination, date, return_date=return_date)
    if serp_results:
        print(f"[Flight Search] Found {len(serp_results)} flights via SerpAPI")
        return serp_results

    # Fallback to web search - return mock data structure for LLM to fill
    print(f"[Flight Search] Using web search fallback for {origin} -> {destination}")
    web_results = exa_search(f"flights from {origin} to {destination} {date} price airlines", num_results=5)

    # If web search also fails, return minimal structure
    if not web_results:
        return [{"title": "Flight search available", "snippet": f"Web search for flights from {origin} to {destination} on {date}"}]

    return web_results


def search_hotels(destination: str, check_in: str, style: str = "luxury") -> list:
    """
    Search hotels - tries SerpAPI first (real Google Hotels data), then Exa web search.
    """
    from utils.travel_api import search_hotels_serp

    # Try SerpAPI first (real hotel data from Google Hotels)
    serp_results = search_hotels_serp(destination, check_in, check_in)
    if serp_results:
        print(f"[Hotel Search] Found {len(serp_results)} hotels via SerpAPI")
        return serp_results

    # Fallback to web search
    query = f"best {style} hotels in {destination} booking price reviews amenities"
    return exa_search(query, num_results=5)


def search_restaurants(destination: str, dietary: str = "") -> list:
    """
    Search restaurants - tries SerpAPI first (real Google Maps data), then Exa web search.
    """
    from utils.travel_api import search_restaurants_serp

    # Try SerpAPI first (real restaurant data from Google Maps)
    serp_results = search_restaurants_serp(destination)
    if serp_results:
        print(f"[Restaurant Search] Found {len(serp_results)} restaurants via SerpAPI")
        return serp_results

    # Fallback to web search
    diet_str = f"{dietary} " if dietary else ""
    query = f"best {diet_str}restaurants in {destination} 2025 2026 address price menu hours"
    return exa_search(query, num_results=8)


def search_attractions(destination: str, vibes: list = None) -> list:
    """
    Search attractions - tries SerpAPI first (real Google Maps data), then Exa web search.
    """
    from utils.travel_api import search_attractions_serp

    # Try SerpAPI first
    serp_results = search_attractions_serp(destination)
    if serp_results:
        print(f"[Attractions Search] Found {len(serp_results)} attractions via SerpAPI")
        return serp_results

    # Fallback to web search
    vibe_str = " ".join(vibes) if vibes else "tourist"
    query = f"top attractions things to do in {destination} {vibe_str} 2025 2026 hours tickets"
    return exa_search(query, num_results=8)


def search_destination_guide(destination: str) -> list:
    """Search for comprehensive destination guides using Exa."""
    query = f"complete travel guide {destination} 2025 2026 transport culture food safety emergency"
    return exa_search(query, num_results=5)
