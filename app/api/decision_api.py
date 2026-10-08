"""
Decision API Router for FoodWaste AI
Endpoints:
POST /decision
"""
from fastapi import APIRouter
from app.schemas.decision_schema import DecisionRequest, DecisionResponse
from app.engines.decision_engine import decision_engine
from app.services.recommendation_service import recommendation_service

router = APIRouter()

@router.post("/decision", response_model=DecisionResponse)
async def run_decision_engine(payload: DecisionRequest):
    """
    Run the Decision Engine independently on arbitrary object-level predictions.
    Input example:
    {
      "objects": [
        {"object": "banana_peel", "category": "Organic", "confidence": 0.96},
        {"object": "plastic_wrapper", "category": "Recyclable", "confidence": 0.94}
      ]
    }
    """
    # Convert Pydantic objects to dicts
    objects_data = [obj.model_dump() for obj in payload.objects]
    
    # Process through decision engine
    decision_result = decision_engine.process(objects_data)
    
    # Enrich with practical recommendation details
    enriched = recommendation_service.enrich_recommendations(decision_result)

    from app.services.impact_service import impact_service
    esg_impact = impact_service.compute_esg_impact(enriched["categories"], enriched["objects_detected"])
    multilingual = impact_service.get_multilingual_guidance(enriched["status"], enriched["categories"])

    return DecisionResponse(
        status=enriched["status"],
        objects_detected=enriched["objects_detected"],
        categories=enriched["categories"],
        recommendation=enriched["recommendation"],
        action_type=enriched["action_type"],
        requires_separation=enriched["requires_separation"],
        multilingual_guidance=multilingual,
        esg_impact=esg_impact
    )
