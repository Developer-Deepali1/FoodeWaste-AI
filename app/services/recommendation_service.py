"""
Recommendation Service for FoodWaste AI
Generates actionable human guidance and bin color associations.
"""
from typing import List, Dict, Any

class RecommendationService:
    CATEGORY_DETAILS = {
        "Organic": {
            "bin": "Green Bin",
            "hex": "#2ecc71",
            "handling": "Suitable for composting or anaerobic digestion. Keep free of inorganic liners."
        },
        "Recyclable": {
            "bin": "Blue Bin",
            "hex": "#3498db",
            "handling": "Rinse containers if soiled. Empty all liquids before putting in recycling."
        },
        "Glass": {
            "bin": "Teal / Glass Bin",
            "hex": "#1abc9c",
            "handling": "Handle with care. If broken, wrap in paper before binning to prevent injury."
        },
        "E-Waste": {
            "bin": "Red / Designated E-Waste Drop-off",
            "hex": "#e74c3c",
            "handling": "Do not put into standard municipal bins. Drop off at certified e-waste collection center."
        },
        "Other": {
            "bin": "Black / Residual Waste Bin",
            "hex": "#95a5a6",
            "handling": "Non-recyclable or composite waste. Dispose in general landfill/residual bin."
        }
    }

    def enrich_recommendations(self, decision_result: Dict[str, Any]) -> Dict[str, Any]:
        """Add bin advice, badges, and practical tips."""
        categories = decision_result.get("categories", [])
        bins_involved = []
        for cat in categories:
            info = self.CATEGORY_DETAILS.get(cat, self.CATEGORY_DETAILS["Other"])
            bins_involved.append({
                "category": cat,
                "bin_name": info["bin"],
                "color": info["hex"],
                "handling_tip": info["handling"]
            })

        decision_result["bin_guidance"] = bins_involved
        return decision_result

recommendation_service = RecommendationService()
