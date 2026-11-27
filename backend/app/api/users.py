import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.core.database import get_db
from app.core.permissions import ASSIGNABLE_ROLES
from app.core.security import hash_password
from app.models import Role, User, UserRole
from app.schemas.user import AdminUserCreate, RoleAssign, UserDetail, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


def _detail(db: Session, user: User) -> UserDetail:
    names = db.scalars(
        select(Role.name).join(UserRole, UserRole.role_id == Role.id).where(UserRole.user_id == user.id)
    ).all()
    detail = UserDetail.model_validate(user)
    detail.roles = sorted(names)
    return detail


def _get_role(db: Session, name: str) -> Role:
    if name not in ASSIGNABLE_ROLES:
        raise HTTPException(status_code=400, detail="That role cannot be assigned")
    role = db.scalar(select(Role).where(Role.name == name))
    if role is None:
        raise HTTPException(status_code=400, detail="Role does not exist")
    return role


def _get_org_user(db: Session, user_id: uuid.UUID, org_id: uuid.UUID) -> User:
    # Filtering by organization in the query is what keeps tenants apart
    user = db.scalar(select(User).where(User.id == user_id, User.organization_id == org_id))
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("", response_model=UserDetail, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: AdminUserCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_permission("users:create")),
):
    role = _get_role(db, payload.role)
    email = payload.email.lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(
        organization_id=admin.organization_id,
        email=email,
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.flush()
    db.add(UserRole(user_id=user.id, role_id=role.id))
    db.commit()
    db.refresh(user)
    return _detail(db, user)


@router.get("", response_model=list[UserDetail])
def list_users(
    db: Session = Depends(get_db),
    admin: User = Depends(require_permission("users:read")),
):
    users = db.scalars(
        select(User).where(User.organization_id == admin.organization_id).order_by(User.full_name)
    ).all()
    return [_detail(db, u) for u in users]


@router.patch("/{user_id}", response_model=UserDetail)
def update_user(
    user_id: uuid.UUID,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_permission("users:update")),
):
    user = _get_org_user(db, user_id, admin.organization_id)
    if payload.is_active is False and user.id == admin.id:
        raise HTTPException(status_code=400, detail="You cannot deactivate your own account")
    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.is_active is not None:
        user.is_active = payload.is_active
    db.commit()
    db.refresh(user)
    return _detail(db, user)


@router.post("/{user_id}/roles", response_model=UserDetail)
def add_role(
    user_id: uuid.UUID,
    payload: RoleAssign,
    db: Session = Depends(get_db),
    admin: User = Depends(require_permission("roles:assign")),
):
    user = _get_org_user(db, user_id, admin.organization_id)
    role = _get_role(db, payload.role)
    if db.get(UserRole, (user.id, role.id)) is None:
        db.add(UserRole(user_id=user.id, role_id=role.id))
        db.commit()
    return _detail(db, user)
