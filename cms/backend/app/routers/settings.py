from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, require_roles
from app.models import MenuItem, SiteSetting, User, UserRole
from app.schemas import MenuItemCreate, MenuItemOut, SettingOut, SettingUpdate
from app.services.audit import log_action

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=list[SettingOut])
def list_settings(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return list(db.scalars(select(SiteSetting).order_by(SiteSetting.key)))


@router.put("/{key}", response_model=SettingOut)
def upsert_setting(
    key: str,
    payload: SettingUpdate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin)),
) -> SiteSetting:
    row = db.get(SiteSetting, key)
    if not row:
        row = SiteSetting(key=key, value=payload.value, updated_by_id=user.id)
        db.add(row)
    else:
        row.value = payload.value
        row.updated_by_id = user.id
    log_action(db, user=user, action="update", resource_type="setting", resource_id=key, request=request)
    db.commit()
    db.refresh(row)
    return row


@router.get("/menus/{location}", response_model=list[MenuItemOut])
def list_menu(location: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return list(
        db.scalars(
            select(MenuItem)
            .where(MenuItem.location == location)
            .order_by(MenuItem.sort_order)
        )
    )


@router.post("/menus", response_model=MenuItemOut, status_code=201)
def create_menu_item(
    payload: MenuItemCreate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin)),
) -> MenuItem:
    row = MenuItem(**payload.model_dump())
    db.add(row)
    log_action(db, user=user, action="create", resource_type="menu", resource_id=row.id, request=request)
    db.commit()
    db.refresh(row)
    return row


@router.delete("/menus/{item_id}")
def delete_menu_item(
    item_id: str,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin)),
) -> dict:
    row = db.get(MenuItem, item_id)
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(row)
    log_action(db, user=user, action="delete", resource_type="menu", resource_id=item_id, request=request)
    db.commit()
    return {"success": True}
