import hashlib
import hmac
import json
from datetime import datetime, timezone

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Webhook, WebhookDelivery


def _sign_payload(secret: str, body: bytes) -> str:
    return hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


def dispatch_event(db: Session, event: str, payload: dict) -> list[dict]:
    hooks = list(
        db.scalars(
            select(Webhook).where(Webhook.is_active.is_(True))
        )
    )
    results: list[dict] = []
    envelope = {
        "event": event,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": payload,
    }
    body = json.dumps(envelope).encode()
    for hook in hooks:
        if event not in (hook.events or []):
            continue
        headers = {
            "Content-Type": "application/json",
            "X-CMS-Event": event,
            "X-CMS-Signature": _sign_payload(hook.secret, body),
        }
        success = False
        status_code = None
        response_text = ""
        try:
            with httpx.Client(timeout=12.0) as client:
                res = client.post(hook.url, content=body, headers=headers)
            status_code = res.status_code
            response_text = res.text[:2000]
            success = 200 <= res.status_code < 300
        except Exception as exc:
            response_text = str(exc)[:2000]
        delivery = WebhookDelivery(
            webhook_id=hook.id,
            event=event,
            status_code=status_code,
            success=success,
            response_body=response_text,
        )
        db.add(delivery)
        results.append({"webhook": hook.name, "success": success, "status": status_code})
    db.commit()
    return results
