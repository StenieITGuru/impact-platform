import sys
from getpass import getpass

from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.permissions import ASSIGNABLE_ROLES
from app.core.security import hash_password
from app.models import Organization, Role, User, UserRole


def main() -> None:
    if len(sys.argv) != 4:
        print('Usage: python -m app.scripts.create_user "ORGANIZATION NAME" EMAIL ROLE_NAME')
        return
    org_name, email, role_name = sys.argv[1], sys.argv[2].lower(), sys.argv[3]
    if role_name not in ASSIGNABLE_ROLES:
        print(f"Role must be one of: {', '.join(ASSIGNABLE_ROLES)}")
        return
    full_name = input("Full name: ").strip()
    password = getpass("Password (min 10 characters): ")
    if len(password) < 10:
        print("Password too short")
        return
    with SessionLocal() as db:
        org = db.scalar(select(Organization).where(Organization.name == org_name))
        role = db.scalar(select(Role).where(Role.name == role_name))
        if org is None or role is None:
            print("Organization or role not found")
            return
        if db.scalar(select(User).where(User.email == email)):
            print("Email already registered")
            return
        user = User(
            organization_id=org.id, email=email, full_name=full_name,
            password_hash=hash_password(password),
        )
        db.add(user)
        db.flush()
        db.add(UserRole(user_id=user.id, role_id=role.id))
        db.commit()
    print(f"Created {email} in {org_name} as {role_name}")


if __name__ == "__main__":
    main()
