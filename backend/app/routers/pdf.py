import uuid
import re
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from pydantic import BaseModel
from app.database.connection import Database
from app.services.pdf_service import PDFService
from app.utils.deps import get_current_user

router = APIRouter(prefix="", tags=["PDF Generation"])

class GeneratePdfSchema(BaseModel):
    trip_id: str

@router.get("/pdfs")
def get_user_pdfs(current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]

    pdfs = Database.fetch_all(
        """
        SELECT gp.id, gp.trip_id, gp.pdf_path, gp.created_at,
               t.source, t.destination
        FROM generated_pdf gp
        JOIN trips t ON gp.trip_id = t.id
        WHERE t.user_id = %s
        ORDER BY gp.created_at DESC
        """,
        (user_id,),
    )

    return [
        {
            "id": pdf["id"],
            "trip_id": pdf["trip_id"],
            "file_name": pdf["pdf_path"],
            "source": pdf["source"],
            "destination": pdf["destination"],
            "created_at": str(pdf["created_at"]),
        }
        for pdf in pdfs
    ]

@router.post("/generate-pdf")
def generate_pdf(data: GeneratePdfSchema, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    
    # 1. Fetch trip and history records
    trip = Database.fetch_one(
        "SELECT * FROM trips WHERE id = %s AND user_id = %s",
        (data.trip_id, user_id)
    )
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found"
        )
        
    history = Database.fetch_one(
        "SELECT * FROM trip_history WHERE trip_id = %s",
        (data.trip_id,)
    )
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip history details not found"
        )
        
    try:
        import json
        details = json.loads(history["generated_response"])
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to parse trip itinerary data"
        )
        
    trip_data = {
        "source": trip["source"],
        "destination": trip["destination"],
        "start_date": str(trip["start_date"]),
        "end_date": str(trip["end_date"]),
        "budget": float(trip["budget"]),
        "details": details
    }
    
    try:
        pdf_buffer = PDFService.generate_trip_pdf(trip_data)

        pdf_id = str(uuid.uuid4())
        pdf_filename = (
            f"trippilot_{trip['source']}_to_{trip['destination']}.pdf"
            .lower()
            .replace(" ", "_")
        )
        pdf_filename = re.sub(r"[^\w.\-]", "", pdf_filename)

        Database.execute(
            """
            INSERT INTO generated_pdf (id, trip_id, pdf_path)
            VALUES (%s, %s, %s)
            """,
            (pdf_id, data.trip_id, pdf_filename),
        )

        return Response(
            content=pdf_buffer.getvalue(),
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{pdf_filename}"'},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF generation failed: {e}"
        )
