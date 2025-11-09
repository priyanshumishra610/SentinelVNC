"""
TOTP (Time-based One-Time Password) for 2FA
"""
import pyotp
import qrcode
from io import BytesIO
import base64
from backend.config import settings


def generate_totp_secret() -> str:
    """Generate a new TOTP secret"""
    return pyotp.random_base32()


def get_totp_uri(username: str, secret: str) -> str:
    """Get TOTP URI for QR code generation"""
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(
        name=username,
        issuer_name=settings.TOTP_ISSUER
    )


def generate_qr_code(uri: str) -> str:
    """Generate QR code as base64 string"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"


def verify_totp(secret: str, token: str) -> bool:
    """Verify a TOTP token"""
    totp = pyotp.TOTP(secret)
    return totp.verify(token, valid_window=settings.TOTP_VALIDITY_WINDOW)

