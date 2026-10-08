"""
Image Service for FoodWaste AI
Handles preprocessing, validation, and resizing.
"""
import io
from PIL import Image
from fastapi import UploadFile, HTTPException

class ImageService:
    @staticmethod
    async def process_upload(file: UploadFile) -> Image.Image:
        """Read and validate uploaded image file."""
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Uploaded file must be an image (JPEG, PNG, WebP).")
        
        content = await file.read()
        try:
            from PIL import ImageOps
            raw_img = Image.open(io.BytesIO(content))
            image = ImageOps.exif_transpose(raw_img).convert("RGB")
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid image file or format.")

        # Step 3 in pipeline: Basic quality check and resize if oversized
        max_dim = 1280
        if max(image.size) > max_dim:
            image.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)

        return image

image_service = ImageService()
