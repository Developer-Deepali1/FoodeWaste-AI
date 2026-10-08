"""
FoodWaste AI - ESG Impact & Multi-Lingual Guidance Service
Calculates environmental footprint saved (CO2e, Water, Landfill diversion)
and provides localized vernacular translations (English, Hindi, Odia).
"""
from typing import List, Dict, Any

class ImpactService:
    # Empirical ecological savings metrics per kg of segregated waste stream
    IMPACT_COEFFICIENTS = {
        "Organic": {
            "co2e_saved_kg": 1.90,     # Methane mitigation vs landfill decomposition
            "water_saved_l": 4.20,      # Soil moisture retention via compost
            "landfill_diversion_pts": 25,
            "compost_potential_kg": 0.45
        },
        "Recyclable": {
            "co2e_saved_kg": 1.55,     # Virgin resin / aluminium smelting offset
            "water_saved_l": 5.80,      # Industrial cooling & manufacturing offset
            "landfill_diversion_pts": 35,
            "circular_economy_score": 92
        },
        "Glass": {
            "co2e_saved_kg": 0.35,     # Furnace energy reduction via cullet
            "water_saved_l": 1.20,
            "landfill_diversion_pts": 20,
            "infinite_recyclability": True
        },
        "E-Waste": {
            "co2e_saved_kg": 2.80,     # Mineral mining & toxic leachate prevention
            "water_saved_l": 12.50,
            "landfill_diversion_pts": 40,
            "heavy_metal_diverted_g": 18.0
        },
        "Other": {
            "co2e_saved_kg": 0.10,
            "water_saved_l": 0.50,
            "landfill_diversion_pts": 5
        }
    }

    def compute_esg_impact(self, categories: List[str], object_count: int) -> Dict[str, Any]:
        """Compute ecological impact metrics for detected waste items."""
        total_co2e = 0.0
        total_water = 0.0
        total_points = 0

        # Estimate average weight of 0.15kg per detected consumer item
        avg_weight = 0.15

        for cat in categories:
            coeffs = self.IMPACT_COEFFICIENTS.get(cat, self.IMPACT_COEFFICIENTS["Other"])
            total_co2e += coeffs["co2e_saved_kg"] * avg_weight * (object_count / max(1, len(categories)))
            total_water += coeffs["water_saved_l"] * avg_weight * (object_count / max(1, len(categories)))
            total_points += coeffs["landfill_diversion_pts"]

        diversion_rate = min(100, int((total_points / max(1, len(categories) * 35)) * 100))

        return {
            "co2e_prevented_kg": round(total_co2e, 2),
            "water_conserved_liters": round(total_water, 2),
            "diversion_rate_pct": diversion_rate,
            "eco_points_earned": total_points,
            "esg_grade": "A+" if diversion_rate >= 80 else ("A" if diversion_rate >= 60 else "B")
        }

    def get_multilingual_guidance(self, status: str, categories: List[str]) -> Dict[str, str]:
        """
        Generate translations in English, Hindi, and Odia for grassroots accessibility.
        """
        cats_en = ", ".join(c.lower() for c in categories) if categories else "waste"
        
        if status == "Mixed Waste":
            return {
                "en": f"Mixed waste detected. Please separate {cats_en} before disposing into respective bins.",
                "hi": f"मिश्रित कचरा मिला है। कृपया कचरे को अलग-अलग डिब्बों में डालने से पहले अलग करें।",
                "or": f"ମିଶ୍ରିତ ବର୍ଜ୍ୟବସ୍ତୁ ଚିହ୍ନଟ ହୋଇଛି। ଦୟାକରି ସମ୍ପୃକ୍ତ ଡଷ୍ଟବିନରେ ପକାଇବା ପୂର୍ବରୁ ଅଲଗା କରନ୍ତୁ।"
            }
        elif status == "Uncertain":
            return {
                "en": "AI confidence is insufficient. Please verify waste manually before disposal.",
                "hi": "एआई की सटीकता कम है। कृपया फेंकने से पहले कचरे की स्वयं जांच करें।",
                "or": "ଏଆଇ ନିଶ୍ଚିତତା କମ ଅଛି। ଦୟାକରି ଫିଙ୍ଗିବା ପୂର୍ବରୁ ନିଜେ ଯାଞ୍ଚ କରନ୍ତୁ।"
            }
        elif status == "Special Handling Required":
            return {
                "en": "Unidentified or hazardous waste detected. Requires special handling.",
                "hi": "अज्ञात या खतरनाक कचरा मिला है। इसके लिए विशेष निपटान की आवश्यकता है।",
                "or": "ଅଜଣା କିମ୍ବା ବିପଜ୍ଜନକ ବର୍ଜ୍ୟବସ୍ତୁ। ଏହା ପାଇଁ ସ୍ୱତନ୍ତ୍ର ପରିଚାଳନା ଆବଶ୍ୟକ।"
            }
        else:
            cat_name = categories[0] if categories else "General"
            return {
                "en": f"Safe for single disposal. Dispose directly as {cat_name.lower()} waste.",
                "hi": f"सुरक्षित एकल कचरा। इसे सीधे {cat_name} वाले डिब्बे में डालें।",
                "or": f"ସୁରକ୍ଷିତ ଏକକ ବର୍ଜ୍ୟ। ଏହାକୁ ସିଧାସଳଖ {cat_name} ଡଷ୍ଟବିନରେ ପକାନ୍ତୁ।"
            }

impact_service = ImpactService()
