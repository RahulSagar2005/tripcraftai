from utils.llm_client import call_llm_json
from utils.exa_search import search_restaurants


def run_food_agent(trip_data: dict) -> dict:
    """
    Food Agent: Recommends restaurants matching dietary preferences and travel style.
    """
    destination = trip_data.get("destination", "")
    dietary = trip_data.get("dietary_restrictions", "")
    travel_style = trip_data.get("travel_style", "comfort")
    vibes = trip_data.get("vibes", [])
    budget = trip_data.get("budget_per_person", 1000)
    currency = trip_data.get("currency", "USD")
    duration = trip_data.get("duration_days", 5)
    additional_info = trip_data.get("additional_info", "")
    transport_pref = trip_data.get("transport_pref", [])

    print(f"[Food Agent] Searching restaurants in {destination} | Dietary: {dietary}")

    results = search_restaurants(destination, dietary)
    context = "\n".join([f"- {r['title']}: {r['snippet']}" for r in results])

    transport_str = ", ".join(transport_pref) if transport_pref else "Public transport"

    prompt = f"""
You are a professional food and dining research agent. Based on real search data, recommend restaurants.

TRIP DETAILS:
- Destination: {destination}
- Dietary restrictions: {dietary if dietary else 'None specified'}
- Travel style: {travel_style}
- Trip vibes: {vibes}
- Budget per person (total trip): {budget} {currency}
- Duration: {duration} days
- Additional info: {additional_info}
- Transport preference: {transport_str}

REAL RESTAURANT SEARCH RESULTS:
{context}

Recommend 6-8 restaurants across different meal types. Be specific and accurate. Include transport notes for reaching each restaurant.

Respond with this exact JSON:
{{
  "intro": "Brief introduction about dining in this destination",
  "restaurants": [
    {{
      "name": "Restaurant Name",
      "cuisine": "Cuisine Type",
      "price_range": "$ / $$ / $$$ / $$$$",
      "price_per_person_approx": 000,
      "currency": "{currency}",
      "meal_type": "Breakfast/Lunch/Dinner/Any",
      "location": "Area/Address",
      "dietary_options": ["vegetarian", "vegan"],
      "highlights": ["highlight1", "highlight2"],
      "must_try": "Dish name",
      "operating_hours": "Hours",
      "reservation_required": true,
      "reservation_info": "Call/Online",
      "rating": 4.5,
      "why_recommended": "One sentence reason"
    }}
  ],
  "dining_tips": ["tip1", "tip2", "tip3"],
  "estimated_daily_food_cost": 000,
  "currency": "{currency}"
}}
"""
    result = call_llm_json(prompt, max_tokens=2500)
    print(f"[Food Agent] Done. Found {len(result.get('restaurants', []))} restaurants.")
    return result
