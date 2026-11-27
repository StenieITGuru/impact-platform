from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Organization
from app.schemas.organization import OrganizationCreate, OrganizationRead

router = APIRouter(prefix="/organizations", tags=["Organizations"])


@router.post("", response_model=OrganizationRead, status_code=status.HTTP_201_CREATED)
def create_organization(payload: OrganizationCreate, db: Session = Depends(get_db)):
    exists = db.scalar(select(Organization).where(Organization.name == payload.name))
    if exists:
        raise HTTPException(status_code=409, detail="An organization with this name already exists")
    org = Organization(name=payload.name, country=payload.country)
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


@router.get("", response_model=list[OrganizationRead])
def list_organizations(db: Session = Depends(get_db)):
    return db.scalars(select(Organization).order_by(Organization.name)).all()
