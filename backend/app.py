# backend/app.py
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os

# Import study planner crew
from backend.studyplanner.crew import StudyPlannerCrew


class MessageIn(BaseModel):
    user_id: str = None
    message: str
    location: str = None
    consent_save: bool = False

app = FastAPI(title="Study Planner API")
# Allow local dev frontend; tighten in production
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

crew = StudyPlannerCrew()

@app.post("/run_session")
async def run_session(payload: MessageIn):
    try:
        result = crew.run_session(
            user_message=payload.message,
            user_id=payload.user_id,
            location=payload.location,
            consent_save=payload.consent_save
        )
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# serve static frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def root():
    return FileResponse("frontend/index.html")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("backend.app:app", host="0.0.0.0", port=port, reload=True)
