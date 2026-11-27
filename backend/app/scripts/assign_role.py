import sys

from sqlalchemy import select

from app.core.database import SessionLocal
from app.models import Role, User, UserRole


def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: python -m app.scripts.assign_role EMAIL ROLE_NAME")
        return
    email, role_name = sys.argv[1].lower(), sys.argv[2]
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == email))
        role = db.scalar(select(Role).where(Role.name == role_name))
        if user is None:
            print(f"No user with email {email}")
            return
        if role is None:
            print(f"No role named {role_name}")
            return
        if db.get(UserRole, (user.id, role.id)):
            print("User already has that role")
            return
        db.add(UserRole(user_id=user.id, role_id=role.id))
        db.commit()
    print(f"Assigned {role_name} to {email}")


if __name__ == "__main__":
    main()
