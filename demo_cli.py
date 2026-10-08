"""
FoodWaste AI - Command Line Interface (CLI) Demo Runner
Allows rapid evaluation of multi-object waste scenarios directly in the terminal.
"""
import sys
import argparse
from pathlib import Path
from PIL import Image

from app.config.settings import settings
from app.services.prediction_service import prediction_service

def run_cli():
    parser = argparse.ArgumentParser(description="🌱 FoodWaste AI - Terminal Evaluation Tool")
    parser.add_argument("--preset", type=str, default="case3", 
                        choices=["case1", "case2", "case3", "case4", "case5", "odisha_canteen"],
                        help="Benchmark scenario to evaluate")
    parser.add_argument("--image", type=str, default=None, 
                        help="Path to custom waste image file")
    
    args = parser.parse_args()

    print("\n" + "=" * 65)
    print("🌱 FOODWASTE AI - MULTI-OBJECT SEGREGATION ENGINE")
    print("=" * 65)

    if args.image and Path(args.image).exists():
        print(f"📷 Processing Image: {args.image}")
        img = Image.open(args.image).convert("RGB")
        result = prediction_service.run_pipeline(img)
    else:
        print(f"✨ Executing Benchmark Scenario: [{args.preset.upper()}]")
        sample_path = Path("app/static/samples")
        preset_file_map = {
            "case1": sample_path / "case1_banana.jpg",
            "case2": sample_path / "case2_recyclables.jpg",
            "case3": sample_path / "case3_mixed.jpg",
            "case4": sample_path / "case4_uncertain.jpg",
            "case5": sample_path / "case5_unknown.jpg",
            "odisha_canteen": sample_path / "odisha_canteen.jpg"
        }
        target_img = preset_file_map.get(args.preset)
        if target_img and target_img.exists():
            img = Image.open(target_img).convert("RGB")
        else:
            img = Image.new("RGB", (640, 480), color=(40, 45, 55))
        
        result = prediction_service.run_pipeline(img, preset_mode=args.preset)

    print("\n🔍 --- INFERENCE & DECISION RESULTS ---")
    print(f"Status:             {result['status']}")
    print(f"Objects Detected:   {result['objects_detected']}")
    print(f"Categories Present: {', '.join(result['categories'])}")
    print(f"Action Type:        {result['action_type']}")
    print(f"Requires Separate:  {result['requires_separation']}")

    print("\n📦 --- OBJECT BREAKDOWN ---")
    for i, obj in enumerate(result['objects'], 1):
        print(f"  {i}. {obj['object'].title()} -> [{obj['category']}] ({int(obj['confidence']*100)}% conf)")

    print("\n💡 --- ACTIONABLE RECOMMENDATION ---")
    print(f"👉 English:  {result['recommendation']}")
    if 'multilingual_guidance' in result:
        print(f"👉 Hindi:    {result['multilingual_guidance'].get('hi', '-')}")
        print(f"👉 Odia:     {result['multilingual_guidance'].get('or', '-')}")

    if 'esg_impact' in result:
        esg = result['esg_impact']
        print("\n🌿 --- ECOLOGICAL ESG IMPACT ---")
        print(f"  • CO2e Emissions Diverted: {esg['co2e_prevented_kg']} kg")
        print(f"  • Industrial Water Saved:  {esg['water_conserved_liters']} L")
        print(f"  • Landfill Diversion Rate: {esg['diversion_rate_pct']}% (Grade {esg['esg_grade']})")

    print("\n" + "=" * 65 + "\n")

if __name__ == "__main__":
    run_cli()
