import json
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.database.connection import Database
from app.utils.deps import get_current_user

router = APIRouter(prefix="", tags=["Trips"])

class SaveTripSchema(BaseModel):
    source: str
    destination: str
    start_date: str
    end_date: str
    budget: float
    travelers: int = 1
    trip_type: str = "Family Trip"
    prompt: str = ""
    details: dict

@router.post("/save-trip")
def save_trip(data: SaveTripSchema, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    trip_id = str(uuid.uuid4())
    history_id = str(uuid.uuid4())

    try:
        Database.execute(
            """
            INSERT INTO trips (id, user_id, source, destination, start_date, end_date, budget)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                trip_id,
                user_id,
                data.source,
                data.destination,
                data.start_date,
                data.end_date,
                float(data.budget),
            ),
        )

        Database.execute(
            """
            INSERT INTO trip_history (id, trip_id, prompt, generated_response)
            VALUES (%s, %s, %s, %s)
            """,
            (
                history_id,
                trip_id,
                data.prompt,
                json.dumps(data.details),
            ),
        )

        return {
            "trip_id": trip_id,
            "message": "Trip saved successfully",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save trip: {e}",
        )

@router.get("/trips")
def get_trips(current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    
    # Retrieve trips, joining with history to get summaries
    trips = Database.fetch_all(
        """
        SELECT t.*, th.generated_response
        FROM trips t
        LEFT JOIN trip_history th ON th.trip_id = t.id
            AND th.created_at = (
                SELECT MAX(created_at) FROM trip_history WHERE trip_id = t.id
            )
        WHERE t.user_id = %s
        ORDER BY t.created_at DESC
        """,
        (user_id,),
    )

    formatted = []
    for t in trips:
        details = {}
        if t.get("generated_response"):
            try:
                details = json.loads(t["generated_response"])
            except Exception:
                pass

        formatted.append({
            "id": str(t["id"]),
            "source": t["source"],
            "destination": t["destination"],
            "start_date": str(t["start_date"]),
            "end_date": str(t["end_date"]),
            "budget": float(t["budget"]),
            "summary": details.get("summary", ""),
            "trip_type": details.get("trip_type", ""),
            "travelers": details.get("travelers"),
            "created_at": str(t["created_at"]),
        })

    return formatted

@router.get("/trip/{trip_id}")
def get_trip_details(trip_id: str, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    
    trip = Database.fetch_one(
        "SELECT * FROM trips WHERE id = %s AND user_id = %s",
        (trip_id, user_id)
    )
    
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )
        
    history = Database.fetch_one(
        """
        SELECT * FROM trip_history
        WHERE trip_id = %s
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (trip_id,),
    )

    details = {}
    if history and history.get("generated_response"):
        try:
            details = json.loads(history["generated_response"])
        except Exception:
            pass

    return {
        "id": str(trip["id"]),
        "source": trip["source"],
        "destination": trip["destination"],
        "start_date": str(trip["start_date"]),
        "end_date": str(trip["end_date"]),
        "budget": float(trip["budget"]),
        "details": details,
    }

@router.delete("/trip/{trip_id}")
def delete_trip(trip_id: str, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    
    trip = Database.fetch_one(
        "SELECT * FROM trips WHERE id = %s AND user_id = %s",
        (trip_id, user_id)
    )
    
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )
        
    Database.execute("DELETE FROM trips WHERE id = %s", (trip_id,))
    return {"message": "Trip deleted successfully"}
