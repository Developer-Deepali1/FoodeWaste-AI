"""
FoodWaste AI - FastAPI Main Application
Intelligent Multi-Object Waste Segregation & Decision-Support System
"""
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config.settings import settings
from app.engines.detection_engine import detection_engine
from app.api import prediction_api, decision_api

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Multi-object waste understanding and segregation decision support system.",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for hackathon demos and external web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers under /api and root as specified in documentation
app.include_router(prediction_api.router, prefix="/api", tags=["Prediction"])
app.include_router(decision_api.router, prefix="/api", tags=["Decision Engine"])

# Root-level endpoints to match exact doc paths (/predict, /decision, /health)
app.include_router(prediction_api.router, tags=["Root API"])
app.include_router(decision_api.router, tags=["Root API"])

@app.get("/health", tags=["System"])
async def health_check():
    """
    Health check endpoint:
    Checks whether backend and model/engine are loaded and ready.
    """
    return {
        "status": "OK",
        "model_loaded": True,
        "yolo_loaded": detection_engine.is_yolo_loaded,
        "mode": "Ultralytics YOLO" if detection_engine.is_yolo_loaded else "Smart Dual-Mode Engine",
        "version": settings.VERSION
    }

# Mount static files for the embedded web dashboard
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

@app.get("/", tags=["Dashboard"])
async def serve_dashboard():
    """Serve the frontend dashboard index.html"""
    index_file = static_path / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "FoodWaste AI Backend is running. Frontend dashboard template not found."}
