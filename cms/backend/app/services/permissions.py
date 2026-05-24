from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import RolePermission, User, UserRole

# Default permission matrix (seeded once)
DEFAULT_PERMISSIONS: dict[UserRole, set[str]] = {
    UserRole.superadmin: {"*"},
    UserRole.admin: {
        "content.read",
        "content.write",
        "content.publish",
        "media.write",
        "contact.read",
        "contact.write",
        "users.read",
        "users.write",
        "settings.write",
        "webhooks.write",
        "roles.write",
        "i18n.write",
    },
    UserRole.editor: {
        "content.read",
        "content.write",
        "media.write",
        "contact.read",
        "contact.write",
        "i18n.read",
    },
    UserRole.viewer: {"content.read", "contact.read", "media.read"},
}


def seed_permissions(db: Session) -> None:
    existing = db.scalar(select(RolePermission.id).limit(1))
    if existing:
        return
    for role, perms in DEFAULT_PERMISSIONS.items():
        if "*" in perms:
            continue
        for perm in perms:
            db.add(RolePermission(role=role, permission=perm, allowed=True))
    db.commit()


def user_has_permission(db: Session, user: User, permission: str) -> bool:
    if user.role == UserRole.superadmin:
        return True
    row = db.scalar(
        select(RolePermission).where(
            RolePermission.role == user.role,
            RolePermission.permission == permission,
            RolePermission.allowed.is_(True),
        )
    )
    if row:
        return True
    return permission in DEFAULT_PERMISSIONS.get(user.role, set())
