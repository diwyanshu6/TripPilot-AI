import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.connection import Database
from app.routers import auth, planner, trips, pdf, profile

app = FastAPI(
    title="TripPilot-AI API",
    description="Multi-Agent AI Travel Itinerary Planner Server using LangGraph, LangChain, and Groq",
    version="1.0.0"
)

# Configure CORS so the React frontend can make requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the actual client domains (e.g. Vercel deployment)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on server startup
@app.on_event("startup")
def startup_db():
    Database.initialize()

# Include Routers
app.include_router(auth.router)
app.include_router(planner.router)
app.include_router(trips.router)
app.include_router(pdf.router)
app.include_router(profile.router)

@app.get("/")
def read_root():
    return {
        "app": "TripPilot-AI API",
        "status": "healthy",
        "message": "Welcome to the TripPilot Multi-Agent travel planner backend server."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
