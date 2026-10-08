"""
Prediction Orchestration Service for FoodWaste AI
Executes full 12-step pipeline:
Image -> Preprocessing -> Multi-Object Detection -> Confidence Analysis -> Decision Engine -> Recommendation -> Logging
"""
import json
import uuid
import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from PIL import Image

from app.config.settings import settings
from app.engines.detection_engine import detection_engine
from app.engines.decision_engine import decision_engine
from app.services.recommendation_service import recommendation_service
from app.utils.image_utils import annotate_image_bboxes, image_to_base64

class PredictionService:
    def __init__(self):
        settings.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        self.log_file = settings.LOGS_DIR / "predictions.jsonl"
        self.feedback_file = settings.LOGS_DIR / "feedback.jsonl"

    def run_pipeline(self, image: Image.Image, preset_mode: Optional[str] = None) -> Dict[str, Any]:
        """Execute full end-to-end multi-object detection and decision pipeline."""
        image_id = str(uuid.uuid4())
        
        # Step 4 & 5: Run Multi-Object Detection
        raw_detections = detection_engine.detect(image, preset_mode=preset_mode)

        # Step 7, 8 & 9: Confidence Analysis & Decision Engine
        decision_result = decision_engine.process(raw_detections)

        # Step 10: Enrich with Recommendation and Bin Guidance
        enriched = recommendation_service.enrich_recommendations(decision_result)

        # Step 10b: Calculate Environmental ESG Impact & Multi-Lingual Guidance
        from app.services.impact_service import impact_service
        esg_impact = impact_service.compute_esg_impact(enriched["categories"], enriched["objects_detected"])
        multilingual = impact_service.get_multilingual_guidance(enriched["status"], enriched["categories"])

        # Step 11: Generate annotated image with bounding boxes
        annotated_img = annotate_image_bboxes(image, raw_detections)
        annotated_b64 = image_to_base64(annotated_img)

        # Format final payload matching the specification
        response_payload = {
            "image_id": image_id,
            "status": enriched["status"],
            "objects_detected": enriched["objects_detected"],
            "categories": enriched["categories"],
            "objects": raw_detections,
            "recommendation": enriched["recommendation"],
            "multilingual_guidance": multilingual,
            "esg_impact": esg_impact,
            "requires_separation": enriched.get("requires_separation", False),
            "action_type": enriched.get("action_type", "DIRECT_DISPOSAL"),
            "confidence_summary": enriched.get("confidence_summary", {}),
            "bin_guidance": enriched.get("bin_guidance", []),
            "annotated_image": annotated_b64,
            "timestamp": datetime.datetime.now().isoformat()
        }

        # Step 12: Log prediction for audit & continuous learning
        self._log_prediction(response_payload)

        return response_payload

    def _log_prediction(self, payload: Dict[str, Any]):
        """Persist prediction record for future retraining/hard-example analysis."""
        try:
            record = {
                "timestamp": payload["timestamp"],
                "image_id": payload["image_id"],
                "objects_detected": payload["objects_detected"],
                "objects": payload["objects"],
                "final_status": payload["status"],
                "recommendation": payload["recommendation"]
            }
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")
        except Exception as e:
            print(f"[PredictionService] Failed to log prediction: {e}")

    def log_feedback(self, feedback_data: Dict[str, Any]):
        """Record user feedback for difficult/hard examples."""
        try:
            feedback_data["logged_at"] = datetime.datetime.now().isoformat()
            with open(self.feedback_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(feedback_data) + "\n")
            return True
        except Exception as e:
            print(f"[PredictionService] Failed to record feedback: {e}")
            return False

    def get_recent_history(self, limit: int = 20) -> list:
        """Fetch recent prediction logs for the audit trail dashboard."""
        if not self.log_file.exists():
            return []
        try:
            records = []
            with open(self.log_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        records.append(json.loads(line.strip()))
            return records[-limit:][::-1]
        except Exception:
            return []

prediction_service = PredictionService()
