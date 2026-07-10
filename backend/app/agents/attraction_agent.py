from app.agents.state import AgentState
from app.tools.tavily_tool import tavily_search
from app.services.llm import call_llm_json

def attraction_agent_node(state: AgentState) -> dict:
    print("Executing Attraction Agent...")
    destination = state.get("destination", "Goa")
    trip_type = state.get("trip_type", "Family Trip")
    
    query = f"top attractions places to visit things to do in {destination} for {trip_type}"
    search_results = tavily_search(query, max_results=5)
    
    prompt = f"""
    You are a travel tour guide assistant. Based on these web search results for tourist spots in {destination}, recommend exactly 5 top attractions that fit a '{trip_type}' style.
    
    Search Results:
    {search_results}
    
    For each attraction, provide:
    1. 'name': Name of the attraction.
    2. 'description': Brief summary of what to see or do.
    3. 'entry_fee': Estimated entry ticket price per person (number/string, e.g. 50 or 'Free').
    4. 'best_time': Best time to visit (e.g. 'Morning', 'Evening', '2 Hours').
    5. 'location': Local area or neighborhood.

    Provide output ONLY as a JSON list matching this structure:
    [
        {{
            "name": "...",
            "description": "...",
            "entry_fee": "Free",
            "best_time": "...",
            "location": "..."
        }},
        ...
    ]
    """
    
    attractions = call_llm_json(prompt)
    
    # Fallback recommendations if LLM fails
    if not attractions:
        attractions = [
            {
                "name": f"{destination} Scenic Overlook",
                "description": "Stunning panoramic vistas of the surrounding region, perfect for sunset views and photography.",
                "entry_fee": "Free",
                "best_time": "Late Evening (4:30 PM - 6:30 PM)",
                "location": "Central Heights"
            },
            {
                "name": f"{destination} Heritage Museum",
                "description": "Exhibits detailing the historical background, cultural evolution, art, and artifacts of the region.",
                "entry_fee": "INR 150",
                "best_time": "Morning (10:00 AM - 1:00 PM)",
                "location": "Old Town"
            },
            {
                "name": f"{destination} Botanical Gardens",
                "description": "Lush green escape featuring native flora, tranquil walking paths, water features, and family picnic areas.",
                "entry_fee": "INR 50",
                "best_time": "Early Morning (8:00 AM - 11:00 AM)",
                "location": "Northside Valley"
            },
            {
                "name": f"Local Spice Plantation & Farm",
                "description": "Guided walking tour through tropical plantations. Includes a traditional buffet lunch and spice tasting.",
                "entry_fee": "INR 500",
                "best_time": "Afternoon (12:00 PM - 3:00 PM)",
                "location": "Suburbs"
            },
            {
                "name": f"{destination} Night Market",
                "description": "Vibrant street market showcasing local crafts, clothing, street food stalls, and live musical performances.",
                "entry_fee": "Free",
                "best_time": "Night (7:00 PM - 11:00 PM)",
                "location": "Downtown Square"
            }
        ]
        
    return {
        "attractions": attractions
    }
