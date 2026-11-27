import uuid
from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

ProjectStatus = Literal["planning", "active", "on_hold", "completed", "cancelled"]


class ProjectCreate(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    description: str | None = None
    donor: str | None = Field(default=None, max_length=200)
    country: str | None = Field(default=None, max_length=100)
    start_date: date | None = None
    end_date: date | None = None
    status: ProjectStatus = "planning"

    @model_validator(mode="after")
    def check_dates(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date cannot be before start_date")
        return self


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=200)
    description: str | None = None
    donor: str | None = Field(default=None, max_length=200)
    country: str | None = Field(default=None, max_length=100)
    start_date: date | None = None
    end_date: date | None = None
    status: ProjectStatus | None = None


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    description: str | None
    donor: str | None
    country: str | None
    start_date: date | None
    end_date: date | None
    status: str


class MemberAdd(BaseModel):
    user_id: uuid.UUID
    role_in_project: str | None = Field(default=None, max_length=100)


class MemberRead(BaseModel):
    user_id: uuid.UUID
    full_name: str
    email: str
    role_in_project: str | None
