"""QR code generation and Cloudinary upload."""

import asyncio
import hashlib
import io

import qrcode
from fastapi import HTTPException, status

from app.services.cloudinary import upload_image_bytes


async def generate_qr_code(url: str) -> str:
    try:
        qr_image = await asyncio.to_thread(_create_qr_image, url)
        url_hash = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
        return await upload_image_bytes(
            qr_image,
            folder="photoshare/qrcodes",
            public_id_prefix=f"qr_{url_hash}",
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate QR code",
        ) from exc


def _create_qr_image(url: str) -> bytes:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    image = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()
