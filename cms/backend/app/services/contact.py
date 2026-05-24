import re
import smtplib
import ssl
from email.message import EmailMessage

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import ContactSubmission

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
URL_RE = re.compile(r"^https?://", re.I)
REGIONS = {"USA", "Canada", "Australia", "Europe", "Other"}


def validate_contact(data: dict) -> list[str]:
    errors: list[str] = []
    if data.get("honeypot"):
        return errors
    if not data.get("name"):
        errors.append("Name is required.")
    if not data.get("email") or not EMAIL_RE.match(data["email"]):
        errors.append("Valid email required.")
    if not data.get("website") or not URL_RE.match(data["website"]):
        errors.append("Website must start with http:// or https://.")
    if data.get("region") not in REGIONS:
        errors.append("Invalid market.")
    if len(data.get("goal", "")) < 12:
        errors.append("Goal text too short.")
    return errors


def send_contact_email(submission: ContactSubmission) -> tuple[bool, str]:
    settings = get_settings()
    host = settings.smtp_host.strip()
    user = settings.smtp_user.strip()
    password = settings.smtp_password.strip()
    if not host or not user or not password:
        return False, "SMTP not configured"

    message = EmailMessage()
    message["Subject"] = f"New SEO inquiry — {submission.name} ({submission.region})"
    message["From"] = user
    message["To"] = settings.contact_notify_to
    message["Reply-To"] = submission.email
    message.set_content(
        "\n".join(
            [
                "New inquiry from seowithfaiz.com",
                "",
                f"Name: {submission.name}",
                f"Email: {submission.email}",
                f"Website: {submission.website}",
                f"Market: {submission.region}",
                "",
                submission.goal,
            ]
        )
    )
    try:
        with smtplib.SMTP(host, settings.smtp_port) as server:
            server.starttls(context=ssl.create_default_context())
            server.login(user, password)
            server.send_message(message)
        return True, "sent"
    except Exception as exc:
        return False, str(exc)


def create_submission(db: Session, data: dict, ip: str = "") -> tuple[ContactSubmission | None, list[str]]:
    if data.get("honeypot"):
        fake = ContactSubmission(
            name="",
            email="bot@blocked.local",
            website="https://example.com",
            region="Other",
            goal="",
            email_delivered=True,
        )
        return fake, []

    errors = validate_contact(data)
    if errors:
        return None, errors

    row = ContactSubmission(
        name=data["name"].strip(),
        email=data["email"].strip(),
        website=data["website"].strip(),
        region=data["region"].strip(),
        goal=data["goal"].strip(),
        ip_address=ip,
    )
    db.add(row)
    db.flush()
    delivered, _ = send_contact_email(row)
    row.email_delivered = delivered
    db.commit()
    db.refresh(row)

    from app.services.email_notify import notify_contact_inquiry
    from app.services.webhooks import dispatch_event

    notify_contact_inquiry(row.name, row.email, row.region)
    dispatch_event(
        db,
        "contact.created",
        {
            "id": row.id,
            "name": row.name,
            "email": row.email,
            "region": row.region,
            "website": row.website,
        },
    )
    return row, []
