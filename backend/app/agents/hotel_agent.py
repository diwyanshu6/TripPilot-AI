from app.agents.state import AgentState
from app.tools.tavily_tool import tavily_search
from app.services.llm import call_llm_json

def hotel_agent_node(state: AgentState) -> dict:
    print("Executing Hotel Agent...")
    destination = state.get("destination", "Goa")
    budget = state.get("budget", 30000.0)
    num_days = state.get("num_days", 5)
    
    # Calculate target hotel budget per night (e.g. 30% of total budget divided by number of nights)
    hotel_budget_limit = (budget * 0.35) / max(num_days - 1, 1)
    
    query = f"best hotels resorts in {destination} under INR {int(hotel_budget_limit)} per night reviews"
    search_results = tavily_search(query, max_results=4)
    
    prompt = f"""
    You are a hotel recommendation assistant. Based on these web search results for hotels in {destination}, extract or recommend exactly 3 hotels that fit a budget of INR {int(hotel_budget_limit)} per night.
    
    Search Results:
    {search_results}
    
    For each hotel, provide:
    1. 'name': Name of the hotel/resort.
    2. 'price_per_night': Estimated cost in INR (number).
    3. 'rating': Star rating or review score (e.g., '4.5/5' or '4 Star').
    4. 'description': Brief summary of amenities, location advantages, etc.
    5. 'link': Booking URL or website link from search results (default to standard official site if not clear).

    Provide output ONLY as a JSON list matching this structure:
    [
        {{
            "name": "...",
            "price_per_night": 3500.0,
            "rating": "4.2/5",
            "description": "...",
            "link": "..."
        }},
        ...
    ]
    """
    
    hotels = call_llm_json(prompt)
    
    # Heuristic fallback if LLM is in simulated mode or fails
    if not hotels:
        hotels = [
            {
                "name": f"Royal {destination} Beach Resort",
                "price_per_night": round(hotel_budget_limit * 0.8),
                "rating": "4.4/5",
                "description": "Premium resort with ocean views, pool access, complimentary breakfast, and free WiFi. Located near main beach attractions.",
                "link": f"https://example.com/resorts/{destination.lower()}-royal"
            },
            {
                "name": f"Palm Tree Boutique Hotel {destination}",
                "price_per_night": round(hotel_budget_limit * 0.6),
                "rating": "4.1/5",
                "description": "Eco-friendly retreat offering cozy cottages, landscaped gardens, an organic restaurant, and guided local tours.",
                "link": f"https://example.com/hotels/{destination.lower()}-palmtree"
            },
            {
                "name": f"Budget Inn {destination} Central",
                "price_per_night": round(hotel_budget_limit * 0.4),
                "rating": "3.9/5",
                "description": "Budget-friendly stay with clean rooms, air conditioning, 24/7 room service, and walking distance to local markets and transport hubs.",
                "link": f"https://example.com/hotels/{destination.lower()}-budgetinn"
            }
        ]
        
    return {
        "hotels": hotels
    }
