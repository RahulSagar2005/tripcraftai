"""
TripCraft AI - Main Agent Orchestrator
Coordinates all agents and returns complete trip plan.
"""

import time
from agents.flight_agent import run_flight_agent
from agents.hotel_agent import run_hotel_agent
from agents.food_agent import run_food_agent
from agents.planner_agent import run_planner_agent, run_destination_guide_agent
from agents.budget_agent import run_budget_agent

# Delay between agent calls to avoid rate limiting (seconds)
AGENT_DELAY = 3


def run_all_agents(trip_data: dict, progress_callback=None) -> dict:
    """
    Orchestrate all AI agents to generate a complete trip plan.

    Args:
        trip_data: dict with all form inputs
        progress_callback: optional callable(step: int, message: str)

    Returns:
        Complete result dict with all sections
    """
    results = {}

    def update(step, msg):
        print(f"[Orchestrator] Step {step}: {msg}")
        if progress_callback:
            progress_callback(step, msg)

    try:
        # Step 1: Flights
        update(1, "Searching for the best flights...")
        flight_data = run_flight_agent(trip_data)
        results["flights"] = flight_data
        time.sleep(AGENT_DELAY)  # Prevent rate limiting

        # Step 2: Hotels
        update(2, "Finding perfect accommodations...")
        hotel_data = run_hotel_agent(trip_data)
        results["hotels"] = hotel_data
        time.sleep(AGENT_DELAY)  # Prevent rate limiting

        # Step 3: Dining
        update(3, "Discovering local dining options...")
        food_data = run_food_agent(trip_data)
        results["dining"] = food_data
        time.sleep(AGENT_DELAY)  # Prevent rate limiting

        # Step 4: Itinerary
        update(4, "Crafting your day-by-day itinerary...")
        itinerary_data = run_planner_agent(trip_data, hotel_data, flight_data, food_data)
        results["itinerary"] = itinerary_data
        time.sleep(AGENT_DELAY)  # Prevent rate limiting

        # Step 5: Destination Guide
        update(5, "Compiling destination guide and tips...")
        guide_data = run_destination_guide_agent(trip_data)
        results["destination_guide"] = guide_data
        time.sleep(AGENT_DELAY)  # Prevent rate limiting

        # Step 6: Budget Analysis
        update(6, "Optimizing your budget...")
        budget_data = run_budget_agent(trip_data, flight_data, hotel_data, food_data)
        results["budget"] = budget_data

        update(7, "Your perfect trip is ready!")
        results["status"] = "success"

    except Exception as e:
        print(f"[Orchestrator ERROR] {e}")
        import traceback
        traceback.print_exc()
        results["status"] = "error"
        results["error_message"] = str(e)

    return results
