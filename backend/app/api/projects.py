import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.core.database import get_db
from app.models import Project, ProjectMember, User
from app.schemas.project import (
    MemberAdd,
    MemberRead,
    ProjectCreate,
    ProjectRead,
    ProjectUpdate,
)

router = APIRouter(prefix="/projects", tags=["Projects"])


def _get_project(db: Session, project_id: uuid.UUID, org_id: uuid.UUID) -> Project:
    # Filtering by organization in the query keeps tenants apart.
    # A project from another organization looks exactly like one that doesn't exist.
    project = db.scalar(
        select(Project).where(Project.id == project_id, Project.organization_id == org_id)
    )
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("projects:create")),
):
    exists = db.scalar(
        select(Project.id).where(
            Project.organization_id == user.organization_id, Project.name == payload.name
        )
    )
    if exists:
        raise HTTPException(status_code=409, detail="A project with this name already exists")
    project = Project(organization_id=user.organization_id, **payload.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("", response_model=list[ProjectRead])
def list_projects(
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("projects:read")),
):
    return db.scalars(
        select(Project)
        .where(Project.organization_id == user.organization_id)
        .order_by(Project.name)
    ).all()


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("projects:read")),
):
    return _get_project(db, project_id, user.organization_id)


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: uuid.UUID,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("projects:update")),
):
    project = _get_project(db, project_id, user.organization_id)
    changes = payload.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(project, field, value)
    if project.start_date and project.end_date and project.end_date < project.start_date:
        raise HTTPException(status_code=400, detail="end_date cannot be before start_date")
    if "name" in changes:
        clash = db.scalar(
            select(Project.id).where(
                Project.organization_id == user.organization_id,
                Project.name == project.name,
                Project.id != project.id,
            )
        )
        if clash:
            raise HTTPException(status_code=409, detail="A project with this name already exists")
    db.commit()
    db.refresh(project)
    return project


@router.get("/{project_id}/members", response_model=list[MemberRead])
def list_members(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("projects:read")),
):
    project = _get_project(db, project_id, user.organization_id)
    rows = db.execute(
        select(ProjectMember, User)
        .join(User, User.id == ProjectMember.user_id)
        .where(ProjectMember.project_id == project.id)
        .order_by(User.full_name)
    ).all()
    return [
        MemberRead(
            user_id=u.id, full_name=u.full_name, email=u.email, role_in_project=m.role_in_project
        )
        for m, u in rows
    ]


@router.post("/{project_id}/members", response_model=MemberRead, status_code=status.HTTP_201_CREATED)
def add_member(
    project_id: uuid.UUID,
    payload: MemberAdd,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("projects:update")),
):
    project = _get_project(db, project_id, user.organization_id)
    member_user = db.scalar(
        select(User).where(User.id == payload.user_id, User.organization_id == user.organization_id)
    )
    if member_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if db.get(ProjectMember, (project.id, member_user.id)):
        raise HTTPException(status_code=409, detail="User is already a member of this project")
    db.add(
        ProjectMember(
            project_id=project.id, user_id=member_user.id, role_in_project=payload.role_in_project
        )
    )
    db.commit()
    return MemberRead(
        user_id=member_user.id,
        full_name=member_user.full_name,
        email=member_user.email,
        role_in_project=payload.role_in_project,
    )
