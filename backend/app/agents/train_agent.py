from app.agents.state import AgentState
from app.tools.train_tool import search_trains

def train_agent_node(state: AgentState) -> dict:
    print("Executing Train Agent...")
    source = state.get("source", "Delhi")
    destination = state.get("destination", "Goa")
    
    trains_list = search_trains(source, destination, limit=5)
    
    return {
        "trains": trains_list
    }
