from utils.llm_client import call_llm_json


def run_budget_agent(trip_data: dict, flight_data: dict, hotel_data: dict, food_data: dict) -> dict:
    """
    Budget Agent: Creates comprehensive budget breakdown and optimization tips.
    """
    destination = trip_data.get("destination", "")
    origin = trip_data.get("origin", "")
    budget_per_person = trip_data.get("budget_per_person", 1000)
    currency = trip_data.get("currency", "USD")
    num_adults = trip_data.get("num_adults", 2)
    duration = trip_data.get("duration_days", 5)
    travel_style = trip_data.get("travel_style", "comfort")
    budget_flexible = trip_data.get("budget_flexible", False)
    transport_pref = trip_data.get("transport_pref", [])
    transport_str = ", ".join(transport_pref) if transport_pref else "Public transport"

    # Extract costs from other agents
    outbound_flights = flight_data.get("outbound_flights", [])
    return_flights = flight_data.get("return_flights", [])
    rec_out_idx = flight_data.get("recommended_outbound_index", 0)
    rec_ret_idx = flight_data.get("recommended_return_index", 0)

    outbound_cost = outbound_flights[rec_out_idx].get("price_per_person", 0) if outbound_flights else 0
    return_cost = return_flights[rec_ret_idx].get("price_per_person", 0) if return_flights else 0
    flight_total_per_person = outbound_cost + return_cost

    hotel = hotel_data.get("recommended_hotel", {})
    hotel_cost_per_night = hotel.get("price_per_night", 0)
    hotel_total = hotel.get("total_cost", hotel_cost_per_night * duration)

    daily_food = food_data.get("estimated_daily_food_cost", 50)
    food_total = daily_food * duration

    total_budget = budget_per_person * num_adults

    prompt = f"""
You are a professional travel budget analyst. Create a detailed budget breakdown and optimization strategy.

TRIP DETAILS:
- {origin} to {destination}
- {duration} days
- {num_adults} adult(s)
- Travel style: {travel_style}
- Total budget: {budget_per_person} {currency} per person ({total_budget} {currency} total)
- Budget flexible: {budget_flexible}
- Transport preference: {transport_str}

ACTUAL COSTS FOUND:
- Flight cost per person (outbound): {outbound_cost} {currency}
- Flight cost per person (return): {return_cost} {currency}
- Total flight per person: {flight_total_per_person} {currency}
- Hotel: {hotel.get('name', 'N/A')} at {hotel_cost_per_night} {currency}/night
- Hotel total ({duration} nights): {hotel_total} {currency}
- Estimated daily food cost: {daily_food} {currency}/person/day
- Total food ({duration} days): {food_total} {currency}/person

Calculate realistic costs for activities, transport, shopping, misc. 
Estimate total per person and compare to budget.

Respond with this JSON:
{{
  "budget_summary": {{
    "budget_per_person": {budget_per_person},
    "currency": "{currency}",
    "total_people": {num_adults},
    "total_budget": {total_budget}
  }},
  "cost_breakdown_per_person": {{
    "flights": {flight_total_per_person},
    "accommodation": 0,
    "food": {food_total},
    "activities": 0,
    "local_transport": 0,
    "shopping_misc": 0,
    "visa_insurance": 0,
    "total_estimated": 0
  }},
  "total_for_group": 0,
  "budget_status": "within_budget / over_budget / significantly_over",
  "overage_amount": 0,
  "savings_tips": [
    {{"tip": "Tip title", "potential_saving": "amount or percentage", "description": "detailed tip"}}
  ],
  "splurge_recommendations": ["thing1 if budget allows"],
  "day_wise_budget": [
    {{"day": 1, "estimated_spend": 0, "breakdown": "Activities + food + transport"}}
  ],
  "currency_tips": ["Exchange rate tip", "ATM tip"],
  "final_recommendation": "One paragraph summary and recommendation"
}}

Fill in the accommodation per person as {hotel_total}/{num_adults} = {round(hotel_total/max(num_adults,1), 0)}.
Calculate all totals accurately.
"""
    result = call_llm_json(prompt, max_tokens=3000)
    print(f"[Budget Agent] Done. Status: {result.get('budget_status', 'N/A')}")
    return result
