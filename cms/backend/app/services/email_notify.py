import smtplib
import ssl
from email.message import EmailMessage

from app.config import get_settings


def send_email(subject: str, body: str, to: str | None = None) -> tuple[bool, str]:
    settings = get_settings()
    host = settings.smtp_host.strip()
    user = settings.smtp_user.strip()
    password = settings.smtp_password.strip()
    recipient = (to or settings.contact_notify_to or "").strip()
    if not host or not user or not password or not recipient:
        return False, "SMTP not configured"

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = user
    message["To"] = recipient
    message.set_content(body)
    try:
        with smtplib.SMTP(host, settings.smtp_port) as server:
            server.starttls(context=ssl.create_default_context())
            server.login(user, password)
            server.send_message(message)
        return True, "sent"
    except Exception as exc:
        return False, str(exc)


def notify_contact_inquiry(name: str, email: str, region: str) -> None:
    send_email(
        f"New inquiry — {name} ({region})",
        f"New contact form submission.\n\nName: {name}\nEmail: {email}\nMarket: {region}\n\nReview in CMS → Inquiries.",
    )


def notify_publish_complete(posts: int, pages: int) -> None:
    send_email(
        "Static publish completed",
        f"CMS published {posts} post(s) and {pages} page(s) to live HTML files.\n\nVerify on site and commit to git if needed.",
    )


def notify_content_published(title: str, content_type: str, locale: str) -> None:
    send_email(
        f"Published: {title} ({locale})",
        f"A {content_type} was published in the CMS.\n\nTitle: {title}\nLocale: {locale}\n\nRun Static publish to write HTML files.",
    )


def notify_content_review(title: str, content_type: str) -> None:
    send_email(
        f"Content ready for review: {title}",
        f"A {content_type} was moved to review status.\n\nTitle: {title}\n\nOpen the CMS to approve and publish.",
    )
