from typing import TypedDict, List, Dict, Any

class AgentState(TypedDict):
    user_prompt: str
    source: str
    destination: str
    start_date: str
    end_date: str
    num_days: int
    budget: float
    travelers: int
    trip_type: str
    run_flight: bool
    run_train: bool
    run_hotel: bool
    run_attractions: bool
    flights: List[Dict[str, Any]]
    trains: List[Dict[str, Any]]
    hotels: List[Dict[str, Any]]
    attractions: List[Dict[str, Any]]
    weather: Dict[str, Any]
    budget_analysis: Dict[str, Any]
    itinerary: List[Dict[str, Any]]
    summary: str
