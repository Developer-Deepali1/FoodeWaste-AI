"""
FoodWaste AI - Configuration Settings
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "FoodWaste AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Model Thresholds
    CONFIDENCE_THRESHOLD: float = 0.60
    HIGH_CONFIDENCE_THRESHOLD: float = 0.85
    UNCERTAIN_THRESHOLD: float = 0.50
    
    # Paths
    BASE_DIR: Path = BASE_DIR
    MODEL_DIR: Path = BASE_DIR / "models" / "waste_detector"
    MODEL_PATH: Path = MODEL_DIR / "best.pt"
    STATIC_DIR: Path = BASE_DIR / "static"
    LOGS_DIR: Path = BASE_DIR / "logs"
    
    # Categories definition based on FoodWaste AI specification
    CATEGORIES: list[str] = [
        "Organic",
        "Recyclable",
        "Glass",
        "E-Waste",
        "Other"
    ]
    
    # Mapping of specific objects to their category
    OBJECT_TO_CATEGORY: dict[str, str] = {
        # Organic (Including Indian/Odisha staple foods and regional waste)
        "banana_peel": "Organic",
        "vegetable_waste": "Organic",
        "fruit_waste": "Organic",
        "cooked_food": "Organic",
        "rice": "Organic",
        "chawal": "Organic",
        "dal": "Organic",
        "roti": "Organic",
        "sabzi": "Organic",
        "coconut_shell": "Organic",
        "eggshell": "Organic",
        "leaves": "Organic",
        "sal_leaf_plate": "Organic",
        "dona": "Organic",
        "apple_core": "Organic",
        "bread": "Organic",
        "tea_leaves": "Organic",
        "chai_patra": "Organic",
        "samosa_crust": "Organic",
        "onion_peel": "Organic",
        "curry_leaves": "Organic",
        
        # Recyclable (Including Indian snacks and beverages)
        "plastic_bottle": "Recyclable",
        "plastic_wrapper": "Recyclable",
        "pet_container": "Recyclable",
        "paper": "Recyclable",
        "cardboard": "Recyclable",
        "aluminium_can": "Recyclable",
        "plastic_cup": "Recyclable",
        "polythene_bag": "Recyclable",
        "metal_cap": "Recyclable",
        "biscuit_wrapper": "Recyclable",
        "chips_packet": "Recyclable",
        "gutkha_sachet": "Recyclable",
        "chutney_pouch": "Recyclable",
        "milk_pouch": "Recyclable",
        "frooti_box": "Recyclable",
        "tetra_pak": "Recyclable",
        "parle_g_wrapper": "Recyclable",
        
        # Glass
        "glass_bottle": "Glass",
        "glass_container": "Glass",
        "broken_glass": "Glass",
        "glass_jar": "Glass",
        "chai_glass": "Glass",
        
        # E-Waste
        "battery": "E-Waste",
        "charger": "E-Waste",
        "cable": "E-Waste",
        "earphones": "E-Waste",
        "small_electronic_components": "E-Waste",
        "circuit_board": "E-Waste",
        
        # Other
        "thermocol": "Other",
        "ceramic": "Other",
        "rubber": "Other",
        "cloth": "Other",
        "jute_sack": "Other",
        "unknown_waste": "Other",
        "unidentified_item": "Other"
    }

    model_config = SettingsConfigDict(case_sensitive=True)

settings = Settings()
