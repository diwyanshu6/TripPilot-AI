import re
from datetime import datetime, timedelta
from app.agents.state import AgentState
from app.services.llm import call_llm_json

NEARBY_CITY_PAIRS = {
    frozenset({"mumbai", "pune"}),
    frozenset({"delhi", "agra"}),
    frozenset({"delhi", "noida"}),
    frozenset({"delhi", "gurgaon"}),
    frozenset({"bangalore", "mysore"}),
    frozenset({"chennai", "pondicherry"}),
    frozenset({"kolkata", "digha"}),
    frozenset({"hyderabad", "warangal"}),
}


def _normalize_city(name: str) -> str:
    return name.strip().lower().split(",")[0].strip()


def decide_agent_plan(source: str, destination: str, budget: float, num_days: int, trip_type: str) -> dict:
    src = _normalize_city(source)
    dst = _normalize_city(destination)
    same_city = src == dst
    nearby = frozenset({src, dst}) in NEARBY_CITY_PAIRS

    run_flight = False
    run_train = False
    run_hotel = num_days >= 1
    run_attractions = True

    if not same_city:
        if nearby:
            run_train = True
        elif budget >= 18000:
            run_flight = True
        else:
            run_train = True

        if budget >= 50000 and not nearby:
            run_flight = True
            run_train = True

    if trip_type.lower() in {"adventure", "backpacking"} and budget < 20000:
        run_flight = False

    print(
        "Supervisor agent plan:",
        f"flight={run_flight}, train={run_train}, hotel={run_hotel}, attractions={run_attractions}",
    )

    return {
        "run_flight": run_flight,
        "run_train": run_train,
        "run_hotel": run_hotel,
        "run_attractions": run_attractions,
    }


def supervisor_node(state: AgentState) -> dict:
    print("Executing Supervisor Agent...")
    prompt = state.get("user_prompt", "")

    # Use structured form data when already provided
    if state.get("source") and state.get("destination") and state.get("start_date") and state.get("end_date"):
        start_date = state["start_date"]
        end_date = state["end_date"]
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            num_days = max((end_dt - start_dt).days + 1, 1)
        except Exception:
            num_days = state.get("num_days") or 5

        return {
            "source": state["source"],
            "destination": state["destination"],
            "start_date": start_date,
            "end_date": end_date,
            "num_days": num_days,
            "budget": float(state.get("budget") or 30000.0),
            "travelers": int(state.get("travelers") or 1),
            "trip_type": state.get("trip_type") or "Family Trip",
            **decide_agent_plan(
                state["source"],
                state["destination"],
                float(state.get("budget") or 30000.0),
                num_days,
                state.get("trip_type") or "Family Trip",
            ),
        }

    # Prompt the LLM to extract variables
    system_prompt = """
    You are a travel supervisor assistant. Your task is to extract structured parameters from the user's travel request.
    Extract:
    1. 'source' (e.g., 'Delhi')
    2. 'destination' (e.g., 'Goa')
    3. 'start_date' (YYYY-MM-DD format. If not mentioned, assume tomorrow's date)
    4. 'end_date' (YYYY-MM-DD format. If not mentioned, calculate based on duration, default to start_date + 4 days)
    5. 'num_days' (integer duration. If not mentioned, default to 5)
    6. 'budget' (numeric value. Extract the amount in Rupees/USD, e.g. 30000. Default to 25000 if not specified)
    7. 'trip_type' (e.g., 'Family Trip', 'Solo Trip', 'Adventure', 'Honeymoon', 'Friends Trip'. Default to 'General Trip')

    Provide output ONLY as a JSON object matching this structure:
    {
        "source": "...",
        "destination": "...",
        "start_date": "...",
        "end_date": "...",
        "num_days": 5,
        "budget": 30000.0,
        "trip_type": "..."
    }
    """
    
    # Try calling LLM
    extracted = call_llm_json(prompt, system_prompt)
    
    # Fallbacks if LLM returns empty/invalid data
    source = extracted.get("source") or "Delhi"
    destination = extracted.get("destination") or "Goa"
    num_days = extracted.get("num_days") or 5
    budget = extracted.get("budget") or 30000.0
    trip_type = extracted.get("trip_type") or "Family Trip"
    
    # Clean source/destination names in case they are phrases
    if "from " in source.lower():
        source = source.lower().split("from ")[-1].title()
    if "to " in destination.lower():
        destination = destination.lower().split("to ")[-1].title()
        
    start_date = extracted.get("start_date")
    if not start_date:
        start_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
    end_date = extracted.get("end_date")
    if not end_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = (start_dt + timedelta(days=num_days - 1)).strftime("%Y-%m-%d")
        except Exception:
            end_date = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
            
    # Try regex override for budget and duration from prompt if LLM failed
    if not extracted:
        # Check budget like 30000, 30k, 30,000, ₹30000, rs 30000
        budget_match = re.search(r"(?:rs|inr|₹|\$)\s*(\d+)(?:\s*k)?\b|(\d+)\s*(?:rs|inr|rupees|budget)", prompt, re.I)
        if budget_match:
            val = budget_match.group(1) or budget_match.group(2)
            try:
                budget = float(val)
                if "k" in prompt.lower() and budget < 1000:
                    budget *= 1000
            except ValueError:
                pass
        
        # Check days like 5 days, 5 day, 5-day
        days_match = re.search(r"(\d+)\s*days?\b", prompt, re.I)
        if days_match:
            try:
                num_days = int(days_match.group(1))
            except ValueError:
                pass

        # Try to guess source and destination
        route_match = re.search(r"(?:from\s+)?([a-zA-Z\s]+)\s+to\s+([a-zA-Z\s]+)", prompt, re.I)
        if route_match:
            s_candidate = route_match.group(1).strip()
            d_candidate = route_match.group(2).strip()
            # Clean up trailing words like "5 days" or "on budget"
            s_candidate = re.split(r"\b(for|in|under|on|with|on)\b", s_candidate, flags=re.I)[0].strip()
            d_candidate = re.split(r"\b(for|in|under|on|with|on)\b", d_candidate, flags=re.I)[0].strip()
            if s_candidate:
                source = s_candidate.title()
            if d_candidate:
                destination = d_candidate.title()
                
    return {
        "source": source,
        "destination": destination,
        "start_date": start_date,
        "end_date": end_date,
        "num_days": num_days,
        "budget": budget,
        "travelers": int(state.get("travelers") or 1),
        "trip_type": trip_type,
        **decide_agent_plan(source, destination, budget, num_days, trip_type),
    }
