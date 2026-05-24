from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import User
from app.services.audit import log_action
from app.services.email_notify import notify_publish_complete
from app.services.permissions import user_has_permission
from app.services.publisher import publish_all
from app.services.webhooks import dispatch_event

router = APIRouter(prefix="/publish", tags=["publish"])


class PublishRequest(BaseModel):
    locale: str = "en"


@router.post("/static")
def publish_static(
    payload: PublishRequest,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    if not user_has_permission(db, user, "content.publish"):
        raise HTTPException(status_code=403, detail="Missing content.publish permission")
    try:
        result = publish_all(db, locale=payload.locale)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    notify_publish_complete(result["posts_published"], result["pages_published"])
    dispatch_event(
        db,
        "publish.completed",
        {"locale": payload.locale, **result},
    )
    log_action(
        db,
        user=user,
        action="publish",
        resource_type="site",
        resource_id=None,
        request=request,
        meta=result,
    )
    db.commit()
    return {"success": True, **result}
