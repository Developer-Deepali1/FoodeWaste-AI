"""
Decision Engine Schemas for FoodWaste AI
"""
from typing import List, Optional
from pydantic import BaseModel, Field

class DecisionInputObject(BaseModel):
    object: str = Field(..., description="Object class name, e.g. banana_peel, plastic_wrapper")
    category: Optional[str] = Field(default=None, description="Optional category. If omitted, resolved via taxonomy")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")

class DecisionRequest(BaseModel):
    objects: List[DecisionInputObject] = Field(..., description="List of detected objects to be analyzed by the Decision Engine")

class DecisionResponse(BaseModel):
    status: str = Field(..., description="Status e.g. Single Waste, Mixed Waste, Uncertain, Unknown Waste")
    objects_detected: int = Field(..., description="Count of detected objects")
    categories: List[str] = Field(..., description="Unique categories detected")
    recommendation: str = Field(..., description="Concrete segregation recommendation")
    action_type: str = Field(..., description="Immediate action category: DIRECT_DISPOSAL, SEPARATE_FIRST, MANUAL_VERIFICATION, SPECIAL_HANDLING")
    requires_separation: bool = Field(..., description="True if waste contains multiple incompatible streams")
    multilingual_guidance: Optional[dict] = Field(default=None, description="Localized translations (en, hi, or)")
    esg_impact: Optional[dict] = Field(default=None, description="Environmental footprint metrics (CO2e, Water, Diversion)")

