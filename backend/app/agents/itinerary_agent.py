from app.agents.state import AgentState
from app.services.llm import call_llm_json

def itinerary_agent_node(state: AgentState) -> dict:
    print("Executing Itinerary Agent...")
    destination = state.get("destination", "Goa")
    num_days = state.get("num_days", 5)
    trip_type = state.get("trip_type", "Family Trip")
    hotels = state.get("hotels", [])
    attractions = state.get("attractions", [])
    
    selected_hotel = hotels[0]["name"] if hotels else "Standard Hotel"
    attractions_list = [attr["name"] for attr in attractions]
    
    prompt = f"""
    You are an expert tour operator itinerary compiler. Your task is to organize a day-by-day itinerary for a {num_days}-day trip to {destination} for a '{trip_type}' group.
    
    Hotel selected: {selected_hotel}
    Attractions to distribute: {', '.join(attractions_list)}
    
    Structure the itinerary for exactly {num_days} days.
    For each day, provide:
    1. 'day': integer number.
    2. 'theme': General topic or theme for the day.
    3. 'activities': A list of exactly 3 activities. Each activity must have:
       - 'time': e.g., '09:00 AM', '02:00 PM', '07:00 PM'.
       - 'title': Headline for the activity.
       - 'description': Brief detail of what they will experience.
       - 'location': Where it happens.
       
    Also, write a 3-sentence general 'summary' highlighting the overall vibe of the trip.
    
    Provide output ONLY as a JSON object matching this structure:
    {{
        "summary": "This trip combines the perfect blend of...",
        "itinerary": [
            {{
                "day": 1,
                "theme": "...",
                "activities": [
                    {{
                        "time": "09:00 AM",
                        "title": "...",
                        "description": "...",
                        "location": "..."
                    }},
                    ...
                ]
            }},
            ...
        ]
    }}
    """
    
    compiled = call_llm_json(prompt)
    
    summary = compiled.get("summary")
    itinerary_days = compiled.get("itinerary")
    
    # Fallback itinerary if LLM fails
    if not itinerary_days or not summary:
        summary = f"An amazing {num_days}-day travel itinerary to {destination} optimized for a {trip_type}. Enjoy sightseeing at top local attractions, delicious regional meals, and comfortable hotel stays."
        itinerary_days = []
        for d in range(1, num_days + 1):
            # Pick a subset of attractions for this day
            attr1 = attractions[(d * 2 - 2) % len(attractions)]["name"] if attractions else "Scenic Walk"
            attr2 = attractions[(d * 2 - 1) % len(attractions)]["name"] if attractions else "Local Market"
            
            itinerary_days.append({
                "day": d,
                "theme": f"Exploring {destination} - Vibe & Sightseeing",
                "activities": [
                    {
                        "time": "09:00 AM",
                        "title": f"Visit {attr1}",
                        "description": f"Embark on a guided walkthrough of {attr1}. Learn about the local history, capture beautiful pictures, and enjoy the ambient weather.",
                        "location": attr1
                    },
                    {
                        "time": "02:00 PM",
                        "title": f"Lunch & Sightseeing around {attr2}",
                        "description": f"Dine at a highly rated local eatery, then explore the neighboring streets and key points of interest near {attr2}.",
                        "location": attr2
                    },
                    {
                        "time": "06:00 PM",
                        "title": "Leisure Evening & Relax at Hotel",
                        "description": f"Return to your resort, {selected_hotel}, to relax. Enjoy swimming, beach strolling, or shopping for souvenirs at nearby night markets.",
                        "location": selected_hotel
                    }
                ]
            })
            
    return {
        "summary": summary,
        "itinerary": itinerary_days
    }
