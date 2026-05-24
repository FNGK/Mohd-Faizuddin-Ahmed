from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_roles
from app.models import RolePermission, User, UserRole
from app.schemas import RolePermissionOut, RolePermissionUpdate
from app.services.audit import log_action
from app.services.permissions import DEFAULT_PERMISSIONS, seed_permissions

router = APIRouter(prefix="/roles", tags=["roles"])

ALL_PERMISSIONS = sorted(
    {
        p
        for perms in DEFAULT_PERMISSIONS.values()
        for p in perms
        if p != "*"
    }
    | {
        "content.read",
        "content.write",
        "content.publish",
        "media.read",
        "media.write",
        "contact.read",
        "contact.write",
        "users.read",
        "users.write",
        "settings.write",
        "webhooks.write",
        "roles.write",
        "i18n.read",
        "i18n.write",
    }
)


@router.get("/permissions", response_model=list[RolePermissionOut])
def list_role_permissions(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.admin)),
):
    seed_permissions(db)
    rows = list(db.scalars(select(RolePermission).order_by(RolePermission.role, RolePermission.permission)))
    if rows:
        return rows
    out: list[RolePermissionOut] = []
    for role, perms in DEFAULT_PERMISSIONS.items():
        if "*" in perms:
            continue
        for perm in sorted(perms):
            out.append(
                RolePermissionOut(id=f"{role.value}:{perm}", role=role, permission=perm, allowed=True)
            )
    return out


@router.get("/catalog")
def permission_catalog(user: User = Depends(require_roles(UserRole.admin))):
    return {"permissions": ALL_PERMISSIONS, "roles": [r.value for r in UserRole]}


@router.put("/permissions")
def upsert_permissions(
    updates: list[RolePermissionUpdate],
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.superadmin)),
):
    for item in updates:
        row = db.scalar(
            select(RolePermission).where(
                RolePermission.role == item.role,
                RolePermission.permission == item.permission,
            )
        )
        if row:
            row.allowed = item.allowed
        else:
            db.add(
                RolePermission(
                    role=item.role,
                    permission=item.permission,
                    allowed=item.allowed,
                )
            )
    log_action(db, user=user, action="update", resource_type="roles", resource_id=None, request=request)
    db.commit()
    return {"success": True, "updated": len(updates)}
