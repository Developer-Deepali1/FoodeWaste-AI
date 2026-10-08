"""
Confidence Analysis Engine for FoodWaste AI
Handles confidence verification, threshold checks, and uncertainty detection.
"""
from typing import List, Dict, Any
from app.config.settings import settings

class ConfidenceEngine:
    def __init__(self, confidence_threshold: float = settings.CONFIDENCE_THRESHOLD,
                 uncertain_threshold: float = settings.UNCERTAIN_THRESHOLD):
        self.confidence_threshold = confidence_threshold
        self.uncertain_threshold = uncertain_threshold

    def evaluate_object(self, obj: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate single object confidence:
        Input: {"object": "banana_peel", "category": "Organic", "confidence": 0.96}
        Output: {"status": "High Confidence", "safe_for_decision": true}
        """
        conf = float(obj.get("confidence", 0.0))
        if conf >= self.confidence_threshold:
            return {
                "status": "High Confidence" if conf >= settings.HIGH_CONFIDENCE_THRESHOLD else "Acceptable Confidence",
                "safe_for_decision": True,
                "confidence": conf
            }
        else:
            return {
                "status": "Low Confidence",
                "safe_for_decision": False,
                "action": "Manual Verification",
                "confidence": conf
            }

    def evaluate_scene(self, objects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluate overall scene confidence metrics across all detected objects.
        """
        if not objects:
            return {
                "status": "No Objects Detected",
                "overall_safe": False,
                "avg_confidence": 0.0,
                "low_confidence_count": 0,
                "total_count": 0
            }

        confidences = [float(obj.get("confidence", 0.0)) for obj in objects]
        avg_confidence = sum(confidences) / len(confidences)
        low_confidence_objects = [
            obj for obj in objects if float(obj.get("confidence", 0.0)) < self.confidence_threshold
        ]

        # If any object is critically low (< UNCERTAIN_THRESHOLD) or average is low
        is_uncertain = (
            any(c < self.uncertain_threshold for c in confidences)
            or (len(low_confidence_objects) > 0 and len(objects) == 1)
            or (len(low_confidence_objects) / len(objects) > 0.4)
        )

        return {
            "status": "Uncertain" if is_uncertain else "Confident",
            "overall_safe": not is_uncertain,
            "avg_confidence": round(avg_confidence, 3),
            "min_confidence": round(min(confidences), 3),
            "max_confidence": round(max(confidences), 3),
            "low_confidence_count": len(low_confidence_objects),
            "total_count": len(objects)
        }

confidence_engine = ConfidenceEngine()
