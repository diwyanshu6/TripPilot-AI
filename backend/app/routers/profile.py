from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from app.database.connection import Database
from app.utils.deps import get_current_user

router = APIRouter(prefix="/profile", tags=["Profile"])

@router.get("/stats")
def get_profile_stats(current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    
    # Retrieve user statistics
    trips = Database.fetch_all("SELECT budget, start_date FROM trips WHERE user_id = %s", (user_id,))
    
    total_trips = len(trips)
    total_budget_allocated = sum(float(t["budget"]) for t in trips)
    
    # Check upcoming trips (start_date > today)
    today = datetime.now().date()
    upcoming_count = 0
    for t in trips:
        try:
            # handle both string date format and datetime date object
            sd = t["start_date"]
            if isinstance(sd, str):
                sd = datetime.strptime(sd, "%Y-%m-%d").date()
            if sd > today:
                upcoming_count += 1
        except Exception:
            pass
            
    # Get PDF count
    pdf_count_res = Database.fetch_one(
        """
        SELECT COUNT(gp.id) as count 
        FROM generated_pdf gp
        JOIN trips t ON gp.trip_id = t.id
        WHERE t.user_id = %s
        """,
        (user_id,)
    )
    pdf_count = pdf_count_res["count"] if pdf_count_res else 0
    
    return {
        "total_trips": total_trips,
        "upcoming_trips": upcoming_count,
        "total_budget": total_budget_allocated,
        "generated_pdfs": pdf_count
    }
