import requests
from config import Config


FIRECRAWL_BASE = "https://api.firecrawl.dev/v1"


def scrape_url(url: str, max_chars: int = 3000) -> str:
    """
    Scrape a URL using Firecrawl and return markdown text.
    """
    headers = {
        "Authorization": f"Bearer {Config.FIRECRAWL_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "url": url,
        "formats": ["markdown"],
        "onlyMainContent": True
    }
    try:
        resp = requests.post(f"{FIRECRAWL_BASE}/scrape", headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        content = data.get("data", {}).get("markdown", "")
        return content[:max_chars]
    except Exception as e:
        print(f"[Firecrawl Error] {e}")
        return ""


def scrape_flight_page(url: str) -> str:
    return scrape_url(url, max_chars=2000)


def scrape_hotel_page(url: str) -> str:
    return scrape_url(url, max_chars=2000)
