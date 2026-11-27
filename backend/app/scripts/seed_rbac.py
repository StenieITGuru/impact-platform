from sqlalchemy import delete, select

from app.core.database import SessionLocal
from app.core.permissions import PERMISSIONS, ROLES
from app.models import Permission, Role, RolePermission


def seed() -> None:
    with SessionLocal() as db:
        perms = {}
        for code, description in PERMISSIONS.items():
            perm = db.scalar(select(Permission).where(Permission.code == code))
            if perm is None:
                perm = Permission(code=code, description=description)
                db.add(perm)
            else:
                perm.description = description
            perms[code] = perm

        roles = {}
        for name, spec in ROLES.items():
            role = db.scalar(select(Role).where(Role.name == name))
            if role is None:
                role = Role(name=name, description=spec["description"])
                db.add(role)
            else:
                role.description = spec["description"]
            roles[name] = role

        db.flush()

        for name, spec in ROLES.items():
            role = roles[name]
            db.execute(delete(RolePermission).where(RolePermission.role_id == role.id))
            for code in spec["permissions"]:
                db.add(RolePermission(role_id=role.id, permission_id=perms[code].id))

        db.commit()
    print(f"Seeded {len(PERMISSIONS)} permissions and {len(ROLES)} roles")


if __name__ == "__main__":
    seed()
