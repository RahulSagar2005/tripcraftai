from utils.llm_client import call_llm_json
from utils.exa_search import search_attractions, search_destination_guide


def _generate_fallback_itinerary(trip_data: dict, hotel_data: dict, flight_data: dict, food_data: dict) -> dict:
    """Generate a basic fallback itinerary when LLM fails."""
    destination = trip_data.get("destination", "Destination")
    origin = trip_data.get("origin", "Origin")
    start_date = trip_data.get("start_date", "2026-01-01")
    duration = trip_data.get("duration_days", 3)
    hotel_name = hotel_data.get("recommended_hotel", {}).get("name", "your hotel")

    days = []
    current_date = start_date

    # Day 0 - Arrival day
    days.append({
        "day_number": 0,
        "date": start_date,
        "title": f"Arrival in {destination}",
        "morning": {"time_slots": [{"time": "6:00 AM", "activity": f"Departure from {origin}", "notes": "Arrive at airport 2-3 hours early"}]},
        "afternoon": {"time_slots": [
            {"time": "2:00 PM", "activity": f"Arrive at {destination}", "notes": "Clear immigration and customs"},
            {"time": "3:00 PM", "activity": f"Transfer to {hotel_name}", "notes": "Take a taxi or pre-booked transfer"}
        ]},
        "evening": {"time_slots": [
            {"time": "6:00 PM", "activity": "Check-in and freshen up", "notes": "Rest after long journey"},
            {"time": "8:00 PM", "activity": "Dinner at a nearby restaurant", "notes": "Keep it light for first evening"}
        ]}
    })

    # Generate remaining days with generic structure
    for day_num in range(1, duration):
        days.append({
            "day_number": day_num,
            "date": current_date,
            "title": f"Day {day_num} in {destination}",
            "morning": {"time_slots": [
                {"time": "9:00 AM", "activity": "Breakfast at hotel", "notes": "Start your day with energy"},
                {"time": "10:00 AM", "activity": f"Explore {destination} - Morning sightseeing", "notes": "Visit popular attractions"}
            ]},
            "afternoon": {"time_slots": [
                {"time": "1:00 PM", "activity": "Lunch at local restaurant", "notes": "Try local cuisine"},
                {"time": "3:00 PM", "activity": f"Afternoon exploration in {destination}", "notes": "Continue sightseeing"}
            ]},
            "evening": {"time_slots": [
                {"time": "7:00 PM", "activity": "Dinner", "notes": "Enjoy evening meal"},
                {"time": "9:00 PM", "activity": "Return to hotel", "notes": "Rest for next day"}
            ]}
        })

    return {
        "days": days,
        "general_tips": [f"Research {destination} attractions before visiting", "Keep important documents safe", "Stay hydrated and take breaks"],
        "best_neighborhoods": [f"City center of {destination}", "Tourist district"],
        "transport_notes": f"Use public transport or taxis for getting around {destination}"
    }


def run_planner_agent(trip_data: dict, hotel_data: dict, flight_data: dict, food_data: dict) -> dict:
    """
    Travel Planner Agent: Creates the full day-by-day itinerary + destination guide.
    """
    destination = trip_data.get("destination", "")
    origin = trip_data.get("origin", "")
    start_date = trip_data.get("start_date", "")
    end_date = trip_data.get("end_date", "")
    duration = trip_data.get("duration_days", 5)
    vibes = trip_data.get("vibes", [])
    pace = trip_data.get("pace", "Balanced")
    travel_style = trip_data.get("travel_style", "comfort")
    specific_interests = trip_data.get("specific_interests", "")
    additional_info = trip_data.get("additional_info", "")
    group_type = trip_data.get("group_type", "Partner")
    previous_visit = trip_data.get("previous_visit", "no")
    dietary = trip_data.get("dietary_restrictions", "")
    num_adults = trip_data.get("num_adults", 2)
    transport_pref = trip_data.get("transport_pref", [])
    start_time_pref = trip_data.get("start_time_pref", "normal")

    print(f"[Planner Agent] Building {duration}-day itinerary for {destination}")

    attraction_results = search_attractions(destination, vibes)
    guide_results = search_destination_guide(destination)

    attraction_context = "\n".join([f"- {r['title']}: {r['snippet']}" for r in attraction_results])
    guide_context = "\n".join([f"- {r['title']}: {r['snippet']}" for r in guide_results])

    recommended_hotel = hotel_data.get("recommended_hotel", {})
    hotel_name = recommended_hotel.get("name", "your hotel")
    hotel_location = recommended_hotel.get("location", destination)

    recommended_outbound_idx = flight_data.get("recommended_outbound_index", 0)
    outbound_flights = flight_data.get("outbound_flights", [])
    outbound_flight = outbound_flights[recommended_outbound_idx] if outbound_flights else {}
    arrival_time = outbound_flight.get("arrival_time", "afternoon")

    restaurants_list = [r.get("name", "") for r in food_data.get("restaurants", [])]

    transport_str = ", ".join(transport_pref) if transport_pref else "Public transport"
    start_time_display = "Early bird (6-8 AM)" if start_time_pref == "early" else ("Normal (9-10 AM)" if start_time_pref == "normal" else "Late riser (10+ AM)")

    prompt = f"""
You are an expert travel planner creating a detailed, personalised day-by-day itinerary.

TRIP DETAILS:
- Traveler name: {trip_data.get('traveler_name', 'Traveler')}
- Destination: {destination}
- Origin: {origin}
- Dates: {start_date} to {end_date}
- Duration: {duration} days (Day 0 = travel day, then Day 1 to Day {duration-1})
- Group: {num_adults} adults, {group_type}
- Trip vibes: {vibes}
- Pace preference: {pace}
- Travel style: {travel_style}
- Dietary: {dietary if dietary else 'No restrictions'}
- Specific interests: {specific_interests if specific_interests else 'None'}
- Additional info: {additional_info if additional_info else 'None'}
- First time visiting: {previous_visit}
- Staying at: {hotel_name} ({hotel_location})
- Arrival: {arrival_time}
- Available restaurants: {restaurants_list[:5]}
- Transport preference: {transport_str}
- Daily start time: {start_time_display}

REAL ATTRACTIONS DATA:
{attraction_context}

REAL DESTINATION DATA:
{guide_context}

Create a COMPLETE day-by-day itinerary. Day 0 is the travel/arrival day. Include morning, afternoon, evening for each day with specific times, place names, and practical notes.

IMPORTANT:
- Use the preferred transport mode ({transport_str}) for all transfer recommendations
- Start each day according to the start time preference ({start_time_display})
- Include specific transport instructions (e.g., "Take a private taxi from X to Y" or "Use public metro")

Respond with this exact JSON (all {duration} days including Day 0):
{{
  "days": [
    {{
      "day_number": 0,
      "date": "{start_date}",
      "title": "Arrival in {destination}",
      "morning": {{
        "time_slots": [
          {{"time": "4:00 AM", "activity": "Departure from {origin}", "notes": "Arrive at airport 2-3 hours early"}}
        ]
      }},
      "afternoon": {{
        "time_slots": [
          {{"time": "2:00 PM", "activity": "Arrive at {destination}", "notes": "Clear immigration and customs"}},
          {{"time": "3:00 PM", "activity": "Transfer to {hotel_name}", "notes": "Take a taxi or pre-booked transfer"}}
        ]
      }},
      "evening": {{
        "time_slots": [
          {{"time": "6:00 PM", "activity": "Check-in and freshen up", "notes": "Rest after long journey"}},
          {{"time": "8:00 PM", "activity": "Dinner at a nearby restaurant", "notes": "Keep it light for first evening"}}
        ]
      }}
    }}
  ],
  "general_tips": ["tip1", "tip2", "tip3"],
  "best_neighborhoods": ["area1", "area2"],
  "transport_notes": "Specific transport advice for this destination"
}}

Generate ALL {duration} days (Day 0 through Day {duration-1}). Each day should have 3-5 time slots per section. Make it genuinely useful and specific to {destination}.
"""
    result = call_llm_json(prompt, max_tokens=6000)

    # Check if LLM failed and use fallback
    if result.get("error") or not result.get("days") or len(result.get("days", [])) == 0:
        print(f"[Planner Agent] LLM failed, using fallback itinerary")
        result = _generate_fallback_itinerary(trip_data, hotel_data, flight_data, food_data)

    print(f"[Planner Agent] Done. Generated {len(result.get('days', []))} days.")
    return result


def run_destination_guide_agent(trip_data: dict) -> dict:
    """
    Generates a detailed destination guide.
    """
    destination = trip_data.get("destination", "")
    vibes = trip_data.get("vibes", [])
    travel_style = trip_data.get("travel_style", "comfort")
    dietary = trip_data.get("dietary_restrictions", "")

    print(f"[Guide Agent] Creating destination guide for {destination}")

    guide_results = search_destination_guide(destination)
    context = "\n".join([f"- {r['title']}: {r['snippet']}" for r in guide_results])

    prompt = f"""
You are an expert travel writer. Create a comprehensive destination guide for {destination}.

Real data found:
{context}

User preferences: {travel_style} travel, vibes: {vibes}, dietary: {dietary}

Respond with this JSON:
{{
  "overview": "2-3 paragraph overview of the destination",
  "best_time_to_visit": "Information about when to visit",
  "main_attractions": [
    {{
      "name": "Attraction Name",
      "type": "Museum/Park/Monument etc",
      "location": "Address or area",
      "opening_hours": "Hours",
      "entrance_fee": "Price or Free",
      "highlights": "What makes it special",
      "tips": "Practical tips"
    }}
  ],
  "local_transport": {{
    "options": ["Metro", "Bus", "Taxi", "Walk"],
    "tips": ["tip1", "tip2"],
    "airport_to_city": "How to get from airport to city"
  }},
  "culture_etiquette": ["tip1", "tip2", "tip3"],
  "safety_tips": ["tip1", "tip2"],
  "weather_info": "Weather during travel dates",
  "language_tips": ["tip1", "tip2"],
  "currency_tips": ["tip1", "tip2"],
  "emergency_contacts": {{
    "police": "number",
    "ambulance": "number",
    "tourist_helpline": "number if applicable"
  }}
}}
"""
    result = call_llm_json(prompt, max_tokens=3000)
    print(f"[Guide Agent] Done.")
    return result
