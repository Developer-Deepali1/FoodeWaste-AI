"""
Image utilities for FoodWaste AI
Handles bounding box drawing, base64 conversion, and preprocessing.
"""
import io
import base64
from typing import List, Dict, Any
from PIL import Image, ImageDraw, ImageFont

# Color palette mapped to the 5 primary waste categories
CATEGORY_COLORS = {
    "Organic": (46, 204, 113),       # Emerald Green
    "Recyclable": (52, 152, 219),    # Blue
    "Glass": (26, 188, 156),         # Teal / Turquoise
    "E-Waste": (231, 76, 60),        # Red / Coral
    "Other": (149, 165, 166)         # Gray / Neutral
}

def annotate_image_bboxes(image: Image.Image, objects: List[Dict[str, Any]]) -> Image.Image:
    """Draw bounding boxes, labels, and confidence tags on PIL image."""
    annotated = image.copy().convert("RGB")
    draw = ImageDraw.Draw(annotated)
    w, h = annotated.size

    # Try default font or basic font
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None

    for obj in objects:
        bbox = obj.get("bbox")
        if not bbox or len(bbox) != 4:
            continue

        x1, y1, x2, y2 = bbox
        # Bound clamp
        x1 = max(0, min(w - 1, x1))
        y1 = max(0, min(h - 1, y1))
        x2 = max(0, min(w - 1, x2))
        y2 = max(0, min(h - 1, y2))

        category = obj.get("category", "Other")
        color = CATEGORY_COLORS.get(category, (255, 255, 0))
        label_text = f"{obj.get('object', '').replace('_', ' ').title()} ({int(obj.get('confidence', 0)*100)}%)"

        # Draw bounding rectangle with thickness
        line_width = max(3, int(min(w, h) / 150))
        for i in range(line_width):
            draw.rectangle([x1 - i, y1 - i, x2 + i, y2 + i], outline=color)

        # Draw label background badge
        text_bbox = draw.textbbox((x1, max(0, y1 - 20)), label_text, font=font)
        text_w = text_bbox[2] - text_bbox[0] + 8
        text_h = text_bbox[3] - text_bbox[1] + 6
        badge_y1 = max(0, y1 - text_h)
        badge_y2 = badge_y1 + text_h

        draw.rectangle([x1, badge_y1, x1 + text_w, badge_y2], fill=color)
        draw.text((x1 + 4, badge_y1 + 2), label_text, fill=(255, 255, 255), font=font)

    return annotated

def image_to_base64(image: Image.Image, format: str = "JPEG") -> str:
    """Encode PIL image to base64 data URL."""
    buffered = io.BytesIO()
    image.save(buffered, format=format, quality=85)
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{img_str}"

def base64_to_image(base64_str: str) -> Image.Image:
    """Decode base64 string to PIL image."""
    if "," in base64_str:
        base64_str = base64_str.split(",", 1)[1]
    image_bytes = base64.b64decode(base64_str)
    return Image.open(io.BytesIO(image_bytes)).convert("RGB")
