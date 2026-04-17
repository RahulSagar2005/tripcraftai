from utils.llm_client import call_llm_json
from utils.exa_search import search_hotels


def run_hotel_agent(trip_data: dict) -> dict:
    """
    Hotel Agent: Finds accommodation options matching user preferences.
    """
    destination = trip_data.get("destination", "")
    start_date = trip_data.get("start_date", "")
    end_date = trip_data.get("end_date", "")
    duration = trip_data.get("duration_days", 5)
    travel_style = trip_data.get("travel_style", "comfort")
    budget = trip_data.get("budget_per_person", 1000)
    currency = trip_data.get("currency", "USD")
    num_rooms = trip_data.get("num_rooms", 1)
    num_adults = trip_data.get("num_adults", 2)
    priorities = trip_data.get("priorities", [])
    vibes = trip_data.get("vibes", [])
    amenities = trip_data.get("amenities", [])
    accom_type = trip_data.get("accom_type", [])
    transport_pref = trip_data.get("transport_pref", [])

    print(f"[Hotel Agent] Searching hotels in {destination} ({travel_style} style)")

    hotel_results = search_hotels(destination, start_date, travel_style)
    context = "\n".join([f"- {r['title']}: {r['snippet']}" for r in hotel_results])

    accom_types_str = ", ".join(accom_type) if accom_type else "Hotel"
    amenities_str = ", ".join(amenities) if amenities else "Standard amenities"
    transport_str = ", ".join(transport_pref) if transport_pref else "Public transport"

    prompt = f"""
You are a professional hotel research agent. Based on the real search data below, recommend the best accommodations.

TRIP DETAILS:
- Destination: {destination}
- Check-in: {start_date}
- Check-out: {end_date}
- Duration: {duration} nights
- Travel Style: {travel_style}
- Budget per person: {budget} {currency}
- Rooms needed: {num_rooms}
- Travelers: {num_adults} adult(s)
- Stay priorities: {priorities}
- Trip vibes: {vibes}
- Preferred accommodation type: {accom_types_str}
- Must-have amenities: {amenities_str}
- Transport preference: {transport_str}

REAL HOTEL SEARCH RESULTS:
{context}

Based on this data, provide 3 hotel recommendations with realistic prices. The recommended hotel should match the travel style, budget, and preferred accommodation type.

Respond with this exact JSON:
{{
  "recommended_hotel": {{
    "name": "Hotel Name",
    "type": "Luxury/Boutique/Budget",
    "rating": 4.5,
    "location": "Area, City",
    "price_per_night": 000,
    "currency": "{currency}",
    "total_cost": 000,
    "amenities": ["amenity1", "amenity2"],
    "highlights": ["highlight1", "highlight2"],
    "address": "Full address",
    "booking_url": "https://..."
  }},
  "alternatives": [
    {{
      "name": "Hotel Name",
      "type": "type",
      "rating": 4.0,
      "price_per_night": 000,
      "currency": "{currency}",
      "location": "area",
      "highlights": ["h1"]
    }}
  ],
  "accommodation_tips": ["tip1", "tip2"],
  "total_accommodation_cost": 000,
  "currency": "{currency}"
}}
"""
    result = call_llm_json(prompt, max_tokens=2000)
    print(f"[Hotel Agent] Done. Recommended: {result.get('recommended_hotel', {}).get('name', 'N/A')}")
    return result
