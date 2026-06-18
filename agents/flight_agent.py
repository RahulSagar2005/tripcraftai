from utils.llm_client import call_llm_json
from utils.exa_search import search_flights


def run_flight_agent(trip_data: dict) -> dict:
    """
    Flight Agent: Finds real flight options for the trip.
    """
    origin = trip_data.get("origin", "")
    destination = trip_data.get("destination", "")
    start_date = trip_data.get("start_date", "")
    end_date = trip_data.get("end_date", "")
    budget = trip_data.get("budget_per_person", 1000)
    currency = trip_data.get("currency", "USD")
    num_adults = trip_data.get("num_adults", 1)
    transport_pref = trip_data.get("transport_pref", [])

    print(f"[Flight Agent] Searching flights: {origin} -> {destination} on {start_date}")

    # Fetch real search results.
    # Outbound: origin -> destination on start_date, returning on end_date (round trip).
    # Return:   destination -> origin on end_date (treated as one-way — no return_date).
    outbound_results = search_flights(origin, destination, start_date, return_date=end_date)
    return_results = search_flights(destination, origin, end_date, return_date=None)

    outbound_context = "\n".join([
        f"- {r['title']}: {r['snippet']}" for r in outbound_results
    ])
    return_context = "\n".join([
        f"- {r['title']}: {r['snippet']}" for r in return_results
    ])

    transport_str = ", ".join(transport_pref) if transport_pref else "Public transport"

    prompt = f"""
You are a professional flight research agent. Based on the real search data below, provide accurate flight recommendations.

TRIP DETAILS:
- Origin: {origin}
- Destination: {destination}
- Outbound Date: {start_date}
- Return Date: {end_date}
- Travelers: {num_adults} adult(s)
- Budget per person: {budget} {currency}
- Transport preference: {transport_str}

OUTBOUND FLIGHT SEARCH RESULTS:
{outbound_context}

RETURN FLIGHT SEARCH RESULTS:
{return_context}

Using the above real data, create a JSON response with realistic flight options. Provide 2-3 outbound and 2 return flight options with real airline names and realistic pricing for this route. Include airport transfer tips based on transport preference.

Respond with this exact JSON structure:
{{
  "outbound_flights": [
    {{
      "airline": "Airline Name",
      "flight_number": "XX 123",
      "departure_time": "HH:MM AM/PM",
      "arrival_time": "HH:MM AM/PM",
      "duration": "X hr Y min",
      "stops": 0,
      "price_per_person": 000,
      "currency": "{currency}",
      "booking_class": "Economy/Business",
      "notes": "any notes"
    }}
  ],
  "return_flights": [
    {{
      "airline": "Airline Name",
      "flight_number": "XX 456",
      "departure_time": "HH:MM AM/PM",
      "arrival_time": "HH:MM AM/PM",
      "duration": "X hr Y min",
      "stops": 0,
      "price_per_person": 000,
      "currency": "{currency}",
      "booking_class": "Economy/Business",
      "notes": "any notes"
    }}
  ],
  "recommended_outbound_index": 0,
  "recommended_return_index": 0,
  "total_flight_cost_per_person": 000,
  "booking_tips": ["tip1", "tip2"],
  "sources": {outbound_results[:2]}
}}
"""
    result = call_llm_json(prompt, max_tokens=2000)
    print(f"[Flight Agent] Done. Found {len(result.get('outbound_flights', []))} outbound options.")
    return result
