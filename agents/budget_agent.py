from utils.llm_client import call_llm_json


def _generate_fallback_budget(trip_data: dict, flight_data: dict, hotel_data: dict, food_data: dict) -> dict:
    """Generate a basic fallback budget when LLM fails."""
    destination = trip_data.get("destination", "Destination")
    origin = trip_data.get("origin", "Origin")
    budget_per_person = trip_data.get("budget_per_person", 1000)
    currency = trip_data.get("currency", "USD")
    num_adults = trip_data.get("num_adults", 2)
    duration = trip_data.get("duration_days", 5)
    travel_style = trip_data.get("travel_style", "comfort")
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
    accommodation_per_person = hotel_total / max(num_adults, 1)

    daily_food = food_data.get("estimated_daily_food_cost", 50)
    food_total = daily_food * duration

    # Estimate other costs based on travel style
    style_multipliers = {"budget": 0.7, "comfort": 1.0, "luxury": 1.5}
    multiplier = style_multipliers.get(travel_style, 1.0)

    activities_per_day = 50 * multiplier
    transport_per_day = 20 * multiplier if "Public" in transport_str else 40 * multiplier
    shopping_misc = 100 * multiplier

    activities_total = activities_per_day * duration
    transport_total = transport_per_day * duration
    visa_insurance = 50 if "international" in destination.lower() else 0

    total_per_person = flight_total_per_person + accommodation_per_person + food_total + activities_total + transport_total + shopping_misc + visa_insurance
    total_for_group = total_per_person * num_adults
    total_budget = budget_per_person * num_adults

    if total_per_person <= budget_per_person:
        budget_status = "within_budget"
        overage_amount = 0
    elif total_per_person <= budget_per_person * 1.2:
        budget_status = "over_budget"
        overage_amount = (total_per_person - budget_per_person) * num_adults
    else:
        budget_status = "significantly_over"
        overage_amount = (total_per_person - budget_per_person) * num_adults

    day_wise_budget = []
    for day in range(1, duration + 1):
        day_wise_budget.append({
            "day": day,
            "estimated_spend": activities_per_day + transport_per_day + daily_food,
            "breakdown": f"Activities ({activities_per_day:.0f}) + Transport ({transport_per_day:.0f}) + Food ({daily_food:.0f})"
        })

    return {
        "budget_summary": {
            "budget_per_person": budget_per_person,
            "currency": currency,
            "total_people": num_adults,
            "total_budget": total_budget
        },
        "cost_breakdown_per_person": {
            "flights": round(flight_total_per_person, 2),
            "accommodation": round(accommodation_per_person, 2),
            "food": round(food_total, 2),
            "activities": round(activities_total, 2),
            "local_transport": round(transport_total, 2),
            "shopping_misc": round(shopping_misc, 2),
            "visa_insurance": round(visa_insurance, 2),
            "total_estimated": round(total_per_person, 2)
        },
        "total_for_group": round(total_for_group, 2),
        "budget_status": budget_status,
        "overage_amount": round(overage_amount, 2),
        "savings_tips": [
            {"tip": "Book flights in advance", "potential_saving": "10-20%", "description": "Flight prices typically increase closer to travel date"},
            {"tip": f"Use {transport_str}", "potential_saving": "15-30%", "description": "Public transport is cheaper than taxis or private transfers"},
            {"tip": "Eat at local restaurants", "potential_saving": "20-40%", "description": "Local eateries offer authentic food at lower prices than tourist spots"}
        ],
        "splurge_recommendations": ["Consider one special dinner at a renowned restaurant"] if total_per_person < budget_per_person * 0.8 else [],
        "day_wise_budget": day_wise_budget,
        "currency_tips": [f"Exchange currency before arrival for better rates", "Use ATMs at banks for lower fees"],
        "final_recommendation": f"Your estimated total is {round(total_per_person, 2)} {currency} per person. {'This is within your budget!' if budget_status == 'within_budget' else f'Consider reducing costs by {round(overage_amount/num_adults, 2)} {currency} per person.'}"
    }


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

    # Check if LLM failed and use fallback
    if result.get("error") or not result.get("budget_summary"):
        print(f"[Budget Agent] LLM failed, using fallback budget")
        result = _generate_fallback_budget(trip_data, flight_data, hotel_data, food_data)

    print(f"[Budget Agent] Done. Status: {result.get('budget_status', 'N/A')}")
    return result
