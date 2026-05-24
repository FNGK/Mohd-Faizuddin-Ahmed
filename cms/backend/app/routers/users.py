from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, require_roles
from app.models import User, UserRole
from app.schemas import UserCreate, UserOut, UserUpdate
from app.security import hash_password
from app.services.audit import log_action

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserOut])
def list_users(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin)),
) -> list[User]:
    return list(db.scalars(select(User).order_by(User.created_at.desc())))


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles(UserRole.admin)),
) -> User:
    if db.scalar(select(User).where(User.email == payload.email.lower())):
        raise HTTPException(status_code=400, detail="Email already registered")
    row = User(
        email=payload.email.lower(),
        full_name=payload.full_name,
        role=payload.role,
        is_active=payload.is_active,
        password_hash=hash_password(payload.password),
    )
    db.add(row)
    log_action(db, user=actor, action="create", resource_type="user", resource_id=row.id, request=request)
    db.commit()
    db.refresh(row)
    return row


@router.patch("/{user_id}", response_model=UserOut)
def update_user(
    user_id: str,
    payload: UserUpdate,
    request: Request,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles(UserRole.admin)),
) -> User:
    row = db.get(User, user_id)
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    data = payload.model_dump(exclude_unset=True)
    if "password" in data:
        row.password_hash = hash_password(data.pop("password"))
    if "email" in data and data["email"]:
        data["email"] = data["email"].lower()
    for key, value in data.items():
        setattr(row, key, value)
    log_action(db, user=actor, action="update", resource_type="user", resource_id=row.id, request=request)
    db.commit()
    db.refresh(row)
    return row


@router.delete("/{user_id}")
def delete_user(
    user_id: str,
    request: Request,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles(UserRole.superadmin)),
) -> dict:
    if actor.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    row = db.get(User, user_id)
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(row)
    log_action(db, user=actor, action="delete", resource_type="user", resource_id=user_id, request=request)
    db.commit()
    return {"success": True}
