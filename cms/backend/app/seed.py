from sqlalchemy import select

from app.config import get_settings
from app.database import SessionLocal
from app.migrate import run_migrations
from app.models import SiteSetting, User, UserRole
from app.security import hash_password
from app.services.permissions import seed_permissions


def run_seed() -> None:
    settings = get_settings()
    run_migrations()
    db = SessionLocal()
    try:
        admin = db.scalar(select(User).where(User.email == settings.admin_email.lower()))
        if not admin:
            admin = User(
                email=settings.admin_email.lower(),
                full_name=settings.admin_name,
                role=UserRole.superadmin,
                password_hash=hash_password(settings.admin_password),
                is_active=True,
            )
            db.add(admin)

        seed_permissions(db)

        defaults = {
            "site_name": "SEO With Faiz",
            "site_url": "https://seowithfaiz.com",
            "timezone": "Asia/Kolkata",
            "brand_primary": "#0d7f76",
            "default_locale": "en",
            "supported_locales": ["en", "es", "fr", "de", "ar", "hi"],
        }
        for key, value in defaults.items():
            if not db.get(SiteSetting, key):
                db.add(SiteSetting(key=key, value=value))

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
