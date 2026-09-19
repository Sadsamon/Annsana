from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from PIL import Image, UnidentifiedImageError


def validate_uploaded_image(upload):
    max_size = getattr(
        settings,
        "MAX_UPLOAD_SIZE_BYTES",
        10 * 1024 * 1024,
    )

    if upload.size > max_size:
        raise ValidationError(
            f"Image files must be smaller than "
            f"{max_size // (1024 * 1024)} MB."
        )

    extension = Path(upload.name).suffix.lower()
    allowed_extensions = {".jpg", ".jpeg", ".png", ".webp"}

    if extension not in allowed_extensions:
        raise ValidationError("Unsupported image type.")

    try:
        image = Image.open(upload)
        image.verify()
    except (UnidentifiedImageError, OSError):
        raise ValidationError("Upload a valid image file.")