"""
Prediction Schemas for FoodWaste AI
"""
from typing import List, Optional
from pydantic import BaseModel, Field

class BoundingBox(BaseModel):
    x1: float = Field(..., description="Top-left X coordinate (normalized or pixel)")
    y1: float = Field(..., description="Top-left Y coordinate (normalized or pixel)")
    x2: float = Field(..., description="Bottom-right X coordinate (normalized or pixel)")
    y2: float = Field(..., description="Bottom-right Y coordinate (normalized or pixel)")

class DetectedObject(BaseModel):
    object: str = Field(..., description="Identifier of detected waste object")
    category: str = Field(..., description="Major waste category (Organic, Recyclable, Glass, E-Waste, Other)")
    confidence: float = Field(..., description="Prediction confidence score between 0.0 and 1.0")
    bbox: Optional[List[float]] = Field(default=None, description="[x1, y1, x2, y2] bounding box")
    safe_for_decision: bool = Field(default=True, description="Whether confidence meets threshold for automatic sorting")

class PredictionResponse(BaseModel):
    status: str = Field(..., description="Overall waste status, e.g. Single Waste, Mixed Waste, Uncertain")
    objects_detected: int = Field(..., description="Total count of detected objects")
    categories: List[str] = Field(..., description="Unique list of categories identified")
    objects: List[DetectedObject] = Field(..., description="List of all detected objects")
    recommendation: str = Field(..., description="Actionable waste segregation instruction")
    confidence_summary: dict = Field(default_factory=dict, description="Summary confidence metrics")
    annotated_image: Optional[str] = Field(default=None, description="Base64 encoded annotated image with bboxes")
    image_id: Optional[str] = Field(default=None, description="Unique identifier for the processed image")

class FeedbackRequest(BaseModel):
    image_id: str
    prediction_correct: bool
    user_correction: Optional[str] = None
    notes: Optional[str] = None
