from langgraph.graph import StateGraph, START, END
from app.agents.state import AgentState
from app.agents.supervisor import supervisor_node
from app.agents.flight_agent import flight_agent_node
from app.agents.train_agent import train_agent_node
from app.agents.hotel_agent import hotel_agent_node
from app.agents.attraction_agent import attraction_agent_node
from app.agents.budget_agent import budget_agent_node
from app.agents.itinerary_agent import itinerary_agent_node


def _route_after_supervisor(state: AgentState) -> str:
    if state.get("run_flight"):
        return "flight_agent"
    if state.get("run_train"):
        return "train_agent"
    if state.get("run_hotel"):
        return "hotel_agent"
    if state.get("run_attractions"):
        return "attraction_agent"
    return "budget_agent"


def _route_after_flight(state: AgentState) -> str:
    if state.get("run_train"):
        return "train_agent"
    if state.get("run_hotel"):
        return "hotel_agent"
    if state.get("run_attractions"):
        return "attraction_agent"
    return "budget_agent"


def _route_after_train(state: AgentState) -> str:
    if state.get("run_hotel"):
        return "hotel_agent"
    if state.get("run_attractions"):
        return "attraction_agent"
    return "budget_agent"


def _route_after_hotel(state: AgentState) -> str:
    if state.get("run_attractions"):
        return "attraction_agent"
    return "budget_agent"


def create_planner_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("flight_agent", flight_agent_node)
    workflow.add_node("train_agent", train_agent_node)
    workflow.add_node("hotel_agent", hotel_agent_node)
    workflow.add_node("attraction_agent", attraction_agent_node)
    workflow.add_node("budget_agent", budget_agent_node)
    workflow.add_node("itinerary_agent", itinerary_agent_node)

    workflow.add_edge(START, "supervisor")
    workflow.add_conditional_edges("supervisor", _route_after_supervisor)
    workflow.add_conditional_edges("flight_agent", _route_after_flight)
    workflow.add_conditional_edges("train_agent", _route_after_train)
    workflow.add_conditional_edges("hotel_agent", _route_after_hotel)
    workflow.add_edge("attraction_agent", "budget_agent")
    workflow.add_edge("budget_agent", "itinerary_agent")
    workflow.add_edge("itinerary_agent", END)

    return workflow.compile()


class PlannerService:
    @classmethod
    def run_workflow(cls, trip_request: dict) -> dict:
        graph = create_planner_graph()

        initial_state = {
            "user_prompt": trip_request.get("prompt", ""),
            "source": trip_request.get("source", ""),
            "destination": trip_request.get("destination", ""),
            "start_date": trip_request.get("start_date", ""),
            "end_date": trip_request.get("end_date", ""),
            "num_days": trip_request.get("num_days", 5),
            "budget": float(trip_request.get("budget", 30000.0)),
            "travelers": int(trip_request.get("travelers", 1)),
            "trip_type": trip_request.get("trip_type", "Family Trip"),
            "run_flight": False,
            "run_train": False,
            "run_hotel": False,
            "run_attractions": False,
            "flights": [],
            "trains": [],
            "hotels": [],
            "attractions": [],
            "weather": {},
            "budget_analysis": {},
            "itinerary": [],
            "summary": "",
        }

        try:
            print(f"Starting LangGraph itinerary planner for: '{initial_state['user_prompt']}'")
            final_state = graph.invoke(initial_state)
            return final_state
        except Exception as e:
            print(f"Error in LangGraph workflow execution: {e}")
            raise e
