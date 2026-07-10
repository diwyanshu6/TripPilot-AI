from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.services.planner_service import PlannerService
from app.utils.deps import get_current_user

router = APIRouter(prefix="", tags=["Planner"])

class PlanTripSchema(BaseModel):
    source: str
    destination: str
    start_date: str
    end_date: str
    budget: float
    travelers: int = 1
    trip_type: str = "Family Trip"

@router.post("/plan-trip")
def plan_trip(data: PlanTripSchema, current_user: dict = Depends(get_current_user)):
    prompt = (
        f"Plan a {data.trip_type} for {data.travelers} traveler(s) "
        f"from {data.source} to {data.destination} "
        f"from {data.start_date} to {data.end_date} with a budget of INR {data.budget}."
    )

    try:
        result = PlannerService.run_workflow({
            "prompt": prompt,
            "source": data.source,
            "destination": data.destination,
            "start_date": data.start_date,
            "end_date": data.end_date,
            "budget": data.budget,
            "travelers": data.travelers,
            "trip_type": data.trip_type,
        })
        
        history_payload = {
            "summary": result.get("summary", ""),
            "flights": result.get("flights", []),
            "trains": result.get("trains", []),
            "hotels": result.get("hotels", []),
            "attractions": result.get("attractions", []),
            "budget_analysis": result.get("budget_analysis", {}),
            "itinerary": result.get("itinerary", []),
            "travelers": data.travelers,
            "trip_type": data.trip_type,
        }

        return {
            "source": result.get("source", data.source),
            "destination": result.get("destination", data.destination),
            "start_date": result.get("start_date", data.start_date),
            "end_date": result.get("end_date", data.end_date),
            "budget": float(result.get("budget", data.budget)),
            "travelers": data.travelers,
            "trip_type": result.get("trip_type", data.trip_type),
            "prompt": prompt,
            "details": history_payload,
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating travel plan: {e}"
        )
