from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_client_ip, get_current_user, require_roles
from app.models import ContactSubmission, User, UserRole
from app.schemas import ContactIn, ContactOut, ContactStatusUpdate
from app.services.audit import log_action
from app.services.contact import create_submission

router = APIRouter(tags=["contact"])


@router.post("/contact", status_code=status.HTTP_201_CREATED)
def public_contact(payload: ContactIn, request: Request, db: Session = Depends(get_db)) -> dict:
    data = payload.model_dump()
    row, errors = create_submission(db, data, get_client_ip(request))
    if errors:
        raise HTTPException(status_code=400, detail={"errors": errors})
    return {
        "success": True,
        "message": "Thank you. Your inquiry was received.",
        "emailDelivered": bool(row and row.email_delivered),
    }


@router.get("/submissions", response_model=list[ContactOut])
def list_submissions(
    status_filter: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.editor)),
) -> list[ContactSubmission]:
    q = select(ContactSubmission).order_by(desc(ContactSubmission.created_at))
    if status_filter:
        q = q.where(ContactSubmission.status == status_filter)
    return list(db.scalars(q))


@router.patch("/submissions/{submission_id}", response_model=ContactOut)
def update_submission(
    submission_id: str,
    payload: ContactStatusUpdate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.editor)),
) -> ContactSubmission:
    row = db.get(ContactSubmission, submission_id)
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    row.status = payload.status
    if payload.notes is not None:
        row.notes = payload.notes
    if payload.status == "read" and not row.read_at:
        row.read_at = datetime.now(timezone.utc)
    log_action(
        db,
        user=user,
        action="update",
        resource_type="contact",
        resource_id=submission_id,
        request=request,
    )
    db.commit()
    db.refresh(row)
    return row
