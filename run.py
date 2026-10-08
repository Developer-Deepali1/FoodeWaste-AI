"""
FoodWaste AI - Application Runner
Starts FastAPI web server with embedded dashboard and auto-reload.
"""
import sys
import uvicorn

if __name__ == "__main__":
    print("=" * 60)
    print("🌱 FoodWaste AI – Intelligent Multi-Object Waste Segregation")
    print("🚀 Starting Server on http://localhost:8000")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("=" * 60)
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
