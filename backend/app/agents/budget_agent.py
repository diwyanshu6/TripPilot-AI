from app.agents.state import AgentState
from app.services.llm import call_llm_json

def budget_agent_node(state: AgentState) -> dict:
    print("Executing Budget Agent...")
    budget_limit = state.get("budget", 30000.0)
    num_days = state.get("num_days", 5)
    
    # 1. Transportation cost calculation
    transportation_cost = 0.0
    flights = state.get("flights", [])
    trains = state.get("trains", [])
    
    # Estimate standard transport (e.g., flight if exists, else train, else default)
    if flights:
        # Default mock average flight ticket
        transportation_cost = 6500.0 * 2 # Round trip
    elif trains:
        transportation_cost = 2150.0 * 2 # Round trip AC 3 Tier
    else:
        transportation_cost = 3000.0 # Default local transport
        
    # 2. Accommodation cost calculation
    accommodation_cost = 0.0
    hotels = state.get("hotels", [])
    if hotels:
        # Select first hotel price as baseline
        price_per_night = hotels[0].get("price_per_night", 3000.0)
        accommodation_cost = float(price_per_night) * max(num_days - 1, 1)
    else:
        accommodation_cost = 2500.0 * max(num_days - 1, 1)
        
    # 3. Sightseeing & Activities
    sightseeing_cost = 0.0
    attractions = state.get("attractions", [])
    for attr in attractions:
        fee_str = str(attr.get("entry_fee", "0"))
        import re
        fee_match = re.search(r"\d+", fee_str)
        if fee_match:
            sightseeing_cost += float(fee_match.group(0))
            
    if sightseeing_cost == 0:
        sightseeing_cost = 300.0 * num_days # Default fallback per day
        
    # 4. Food & Miscellaneous expenses
    food_misc_cost = 1000.0 * num_days
    
    # Summing total
    total_estimated = transportation_cost + accommodation_cost + sightseeing_cost + food_misc_cost
    status = "Within Budget"
    if total_estimated > budget_limit:
        status = "Exceeds Budget"
        
    analysis = {
        "transportation_est": transportation_cost,
        "accommodation_est": accommodation_cost,
        "sightseeing_est": sightseeing_cost,
        "food_misc_est": food_misc_cost,
        "total_estimated": total_estimated,
        "allocated_budget": budget_limit,
        "status": status,
        "saving_tips": []
    }
    
    prompt = f"""
    You are a financial travel budget analyzer. Analyze the following cost breakdown against the target budget of INR {budget_limit}.
    
    Breakdown:
    - Transportation: INR {transportation_cost}
    - Accommodation: INR {accommodation_cost}
    - Sightseeing: INR {sightseeing_cost}
    - Food & Misc: INR {food_misc_cost}
    - Total Estimated: INR {total_estimated}
    
    If the total exceeds the budget, provide 3 practical tips to reduce costs (e.g. suggesting trains over flights, choosing budget hotel rooms, visiting free attractions).
    If it is within the budget, provide tips on how they can spend the surplus (e.g. upgrade hotel room, dine at a premium restaurant, go for an extra excursion).
    
    Provide output ONLY as a JSON list of strings (the saving/spending tips), e.g.:
    [
        "Tip 1...",
        "Tip 2..."
    ]
    """
    
    tips = call_llm_json(prompt)
    if not tips:
        if total_estimated > budget_limit:
            tips = [
                "Consider booking train sleeper class or budget flights in advance to save up to 40% on transport.",
                "Swap premium resorts for boutique homestays or budget inns listed in the recommendations.",
                "Prioritize visiting free attractions (like beaches, parks, and temples) over paid plantation tours."
            ]
        else:
            tips = [
                "You have a budget surplus! Consider booking a premium spa treatment at your resort.",
                "Upgrade your accommodation selection to a higher-rated sea-view room.",
                "Set aside some budget for trying premium local cuisines at signature fine-dining restaurants."
            ]
            
    analysis["saving_tips"] = tips
    
    return {
        "budget_analysis": analysis
    }
