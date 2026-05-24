from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, require_roles
from app.models import ContentTranslation, User, UserRole
from app.schemas import TranslationCreate, TranslationOut, TranslationUpdate
from app.services.audit import log_action
from app.services.permissions import user_has_permission

router = APIRouter(prefix="/translations", tags=["i18n"])

SUPPORTED_LOCALES = ["en", "es", "fr", "de", "ar", "hi"]


@router.get("/locales")
def list_locales():
    return {"default": "en", "supported": SUPPORTED_LOCALES}


@router.get("", response_model=list[TranslationOut])
def list_translations(
    content_type: str | None = None,
    parent_id: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = select(ContentTranslation).order_by(ContentTranslation.updated_at.desc())
    if content_type:
        q = q.where(ContentTranslation.content_type == content_type)
    if parent_id:
        q = q.where(ContentTranslation.parent_id == parent_id)
    return list(db.scalars(q))


@router.post("", response_model=TranslationOut, status_code=status.HTTP_201_CREATED)
def create_translation(
    payload: TranslationCreate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.editor)),
):
    if payload.locale not in SUPPORTED_LOCALES:
        raise HTTPException(status_code=400, detail="Unsupported locale")
    if not user_has_permission(db, user, "i18n.write"):
        raise HTTPException(status_code=403, detail="Missing i18n.write")
    existing = db.scalar(
        select(ContentTranslation).where(
            ContentTranslation.content_type == payload.content_type,
            ContentTranslation.parent_id == payload.parent_id,
            ContentTranslation.locale == payload.locale,
        )
    )
    if existing:
        raise HTTPException(status_code=400, detail="Translation exists for locale")
    row = ContentTranslation(**payload.model_dump())
    db.add(row)
    log_action(db, user=user, action="create", resource_type="translation", resource_id=row.id, request=request)
    db.commit()
    db.refresh(row)
    return row


@router.patch("/{translation_id}", response_model=TranslationOut)
def update_translation(
    translation_id: str,
    payload: TranslationUpdate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.editor)),
):
    row = db.get(ContentTranslation, translation_id)
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(row, key, value)
    log_action(db, user=user, action="update", resource_type="translation", resource_id=row.id, request=request)
    db.commit()
    db.refresh(row)
    return row


@router.delete("/{translation_id}")
def delete_translation(
    translation_id: str,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.editor)),
):
    row = db.get(ContentTranslation, translation_id)
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(row)
    log_action(db, user=user, action="delete", resource_type="translation", resource_id=translation_id, request=request)
    db.commit()
    return {"success": True}
