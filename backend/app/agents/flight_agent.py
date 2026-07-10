from app.agents.state import AgentState
from app.tools.flight_tool import search_flights

def flight_agent_node(state: AgentState) -> dict:
    print("Executing Flight Agent...")
    source = state.get("source", "Delhi")
    destination = state.get("destination", "Goa")
    
    query = f"flights from {source} to {destination}"
    flights_list = search_flights(query, limit=5)
    
    return {
        "flights": flights_list
    }
