"""
AI Decision Engine for FoodWaste AI
Converts raw multi-object detections into actionable segregation instructions.

Handles:
- Case 1: Single high-confidence object
- Case 2: Multiple objects with same category
- Case 3: Multiple objects with different categories (Mixed Waste)
- Case 4: Low-confidence prediction (Manual verification required)
- Case 5: Unknown object (Special/manual handling recommended)
"""
from typing import List, Dict, Any
from app.config.settings import settings
from app.engines.confidence_engine import confidence_engine

class DecisionEngine:
    def __init__(self, confidence_threshold: float = settings.CONFIDENCE_THRESHOLD):
        self.confidence_threshold = confidence_threshold

    def resolve_category(self, object_name: str, given_category: str = None) -> str:
        """Resolve category from object name and known taxonomy."""
        if given_category and given_category in settings.CATEGORIES:
            return given_category
        clean_name = object_name.strip().lower().replace(" ", "_")
        return settings.OBJECT_TO_CATEGORY.get(clean_name, "Other")

    def process(self, objects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Main decision-making algorithm implementing Cases 1-5.
        """
        if not objects:
            return {
                "status": "No Waste Detected",
                "objects_detected": 0,
                "categories": [],
                "recommendation": "No waste detected in the frame. Please upload or scan a clearer image.",
                "action_type": "NO_ACTION",
                "requires_separation": False,
                "confidence_summary": {"status": "No Objects"}
            }

        scene_conf = confidence_engine.evaluate_scene(objects)
        
        # Format and validate each object
        normalized_objects = []
        for obj in objects:
            obj_name = obj.get("object", "unknown").strip().lower()
            cat = self.resolve_category(obj_name, obj.get("category"))
            conf = float(obj.get("confidence", 0.0))
            conf_eval = confidence_engine.evaluate_object({"confidence": conf})
            
            normalized_objects.append({
                "object": obj_name,
                "category": cat,
                "confidence": round(conf, 3),
                "safe_for_decision": conf_eval["safe_for_decision"],
                "bbox": obj.get("bbox", None)
            })

        categories = sorted(list(set(o["category"] for o in normalized_objects)))
        total_objects = len(normalized_objects)

        # -------------------------------------------------------------
        # CASE 4: Low-confidence prediction
        # If any single object has low confidence or the scene is uncertain
        # -------------------------------------------------------------
        has_low_conf = any(not o["safe_for_decision"] for o in normalized_objects)
        if has_low_conf or not scene_conf["overall_safe"]:
            low_items = [o["object"] for o in normalized_objects if not o["safe_for_decision"]]
            item_str = ", ".join(low_items) if low_items else "detected object(s)"
            return {
                "status": "Uncertain",
                "objects_detected": total_objects,
                "categories": categories,
                "recommendation": f"AI confidence is insufficient ({scene_conf['avg_confidence']*100:.1f}%) for {item_str}. Verify waste manually.",
                "action_type": "MANUAL_VERIFICATION",
                "requires_separation": False,
                "confidence_summary": scene_conf,
                "normalized_objects": normalized_objects
            }

        # -------------------------------------------------------------
        # CASE 5: Unknown object
        # If detected object is not present in supported known categories or marked "Other"
        # -------------------------------------------------------------
        has_unknown = any(
            o["category"] == "Other" or o["object"] in ["unknown", "unknown_waste", "other"]
            for o in normalized_objects
        )
        if has_unknown:
            unknown_items = [o["object"] for o in normalized_objects if o["category"] == "Other"]
            item_str = ", ".join(unknown_items) if unknown_items else "unidentified item"
            return {
                "status": "Special Handling Required",
                "objects_detected": total_objects,
                "categories": categories,
                "recommendation": f"Unrecognized object ({item_str}) detected. Special or manual handling recommended before bin disposal.",
                "action_type": "SPECIAL_HANDLING",
                "requires_separation": len(categories) > 1,
                "confidence_summary": scene_conf,
                "normalized_objects": normalized_objects
            }

        # -------------------------------------------------------------
        # CASE 1: Single high-confidence object
        # -------------------------------------------------------------
        if total_objects == 1:
            single_obj = normalized_objects[0]
            cat = single_obj["category"]
            obj_name = single_obj["object"].replace("_", " ").title()
            return {
                "status": "Single Waste",
                "objects_detected": 1,
                "categories": [cat],
                "recommendation": f"Dispose as {cat.lower()} waste.",
                "action_type": "DIRECT_DISPOSAL",
                "requires_separation": False,
                "confidence_summary": scene_conf,
                "normalized_objects": normalized_objects
            }

        # -------------------------------------------------------------
        # CASE 2: Multiple objects with SAME category
        # -------------------------------------------------------------
        if len(categories) == 1:
            cat = categories[0]
            items = ", ".join(o["object"].replace("_", " ") for o in normalized_objects)
            return {
                "status": f"Uniform {cat} Waste",
                "objects_detected": total_objects,
                "categories": [cat],
                "recommendation": f"All {total_objects} items are {cat}. Dispose together as {cat.lower()} waste.",
                "action_type": "DIRECT_DISPOSAL",
                "requires_separation": False,
                "confidence_summary": scene_conf,
                "normalized_objects": normalized_objects
            }

        # -------------------------------------------------------------
        # CASE 3: Multiple objects with DIFFERENT categories (Mixed Waste)
        # -------------------------------------------------------------
        cat_lower_list = [c.lower() for c in categories]
        if len(cat_lower_list) == 2:
            cat_str = f"{cat_lower_list[0]} and {cat_lower_list[1]}"
        else:
            cat_str = f"{', '.join(cat_lower_list[:-1])} and {cat_lower_list[-1]}"

        return {
            "status": "Mixed Waste",
            "objects_detected": total_objects,
            "categories": categories,
            "recommendation": f"Separate {cat_str} waste before disposal.",
            "action_type": "SEPARATE_FIRST",
            "requires_separation": True,
            "confidence_summary": scene_conf,
            "normalized_objects": normalized_objects
        }

decision_engine = DecisionEngine()
