import mimetypes
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import UPLOADS_DIR, get_settings
from app.database import get_db
from app.deps import get_current_user, require_roles
from app.models import Media, User, UserRole
from app.schemas import MediaOut
from app.services.audit import log_action

router = APIRouter(prefix="/media", tags=["media"])

ALLOWED = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
    "image/svg+xml",
    "application/pdf",
}
MAX_BYTES = 12 * 1024 * 1024


def media_url(stored_path: str) -> str:
    return f"/api/v1/media/files/{stored_path}"


def to_media_out(row: Media) -> MediaOut:
    return MediaOut(
        id=row.id,
        filename=row.filename,
        stored_path=row.stored_path,
        mime_type=row.mime_type,
        size_bytes=row.size_bytes,
        width=row.width,
        height=row.height,
        alt_text=row.alt_text,
        folder=row.folder,
        url=media_url(row.stored_path),
        created_at=row.created_at,
    )


@router.get("", response_model=list[MediaOut])
def list_media(
    folder: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[MediaOut]:
    q = select(Media).order_by(Media.created_at.desc())
    if folder:
        q = q.where(Media.folder == folder)
    return [to_media_out(m) for m in db.scalars(q)]


@router.post("/upload", response_model=MediaOut, status_code=status.HTTP_201_CREATED)
async def upload_media(
    request: Request,
    file: UploadFile = File(...),
    folder: str = Form("general"),
    alt_text: str | None = Form(None),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.editor)),
) -> MediaOut:
    if not file.content_type or file.content_type not in ALLOWED:
        raise HTTPException(status_code=400, detail="File type not allowed")

    data = await file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=400, detail="File too large (max 12MB)")

    ext = Path(file.filename or "upload").suffix.lower() or mimetypes.guess_extension(file.content_type) or ""
    safe_folder = "".join(c for c in folder if c.isalnum() or c in "-_")[:40] or "general"
    stored_name = f"{safe_folder}/{uuid.uuid4().hex}{ext}"
    dest = UPLOADS_DIR / stored_name
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)

    row = Media(
        filename=file.filename or stored_name,
        stored_path=stored_name.replace("\\", "/"),
        mime_type=file.content_type,
        size_bytes=len(data),
        alt_text=alt_text,
        folder=safe_folder,
        uploaded_by_id=user.id,
    )
    db.add(row)
    log_action(db, user=user, action="upload", resource_type="media", resource_id=row.id, request=request)
    db.commit()
    db.refresh(row)
    return to_media_out(row)


@router.get("/files/{file_path:path}")
def serve_file(file_path: str):
    from fastapi.responses import FileResponse

    target = (UPLOADS_DIR / file_path).resolve()
    if not str(target).startswith(str(UPLOADS_DIR.resolve())) or not target.is_file():
        raise HTTPException(status_code=404, detail="Not found")
    return FileResponse(target)


@router.delete("/{media_id}")
def delete_media(
    media_id: str,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin)),
) -> dict:
    row = db.get(Media, media_id)
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    path = UPLOADS_DIR / row.stored_path
    if path.is_file():
        path.unlink()
    db.delete(row)
    log_action(db, user=user, action="delete", resource_type="media", resource_id=media_id, request=request)
    db.commit()
    return {"success": True}
