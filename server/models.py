from pydantic import BaseModel, EmailStr
from typing import Optional, Literal
from datetime import datetime
from uuid import UUID


# ─────────────────────────────────────────
#  User Models
# ─────────────────────────────────────────

class UserBase:
    """Base User — shared attributes across all roles."""
    def __init__(self, id: str, email: str, full_name: str, role: str):
        self.id = id
        self.email = email
        self.full_name = full_name
        self.role = role

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.full_name} ({self.role})>"


class Student(UserBase):
    """Student — can report lost items and reserve found items."""
    def __init__(self, id, email, full_name, student_id: str = None):
        super().__init__(id, email, full_name, role="student")
        self.student_id = student_id





class Faculty(UserBase):
    """Faculty — manages inventory, verifies claims, views audit log."""
    def __init__(self, id, email, full_name, department: str = None):
        super().__init__(id, email, full_name, role="faculty")
        self.department = department


# ─────────────────────────────────────────
#  Item Model
# ─────────────────────────────────────────

class Item:
    """Represents a lost or found item report."""
    VALID_STATUSES = ["reported", "found", "reserved", "claimed", "closed"]
    VALID_TYPES = ["lost", "found"]

    def __init__(
        self,
        id: str,
        reporter_id: str,
        type: str,
        title: str,
        category: str,
        status: str = "reported",
        description: str = None,
        brand: str = None,
        color: str = None,
        location_found: str = None,
        image_url: str = None,
    ):
        assert type in self.VALID_TYPES, f"type must be one of {self.VALID_TYPES}"
        assert status in self.VALID_STATUSES, f"status must be one of {self.VALID_STATUSES}"
        self.id = id
        self.reporter_id = reporter_id
        self.type = type
        self.title = title
        self.category = category
        self.status = status
        self.description = description
        self.brand = brand
        self.color = color
        self.location_found = location_found
        self.image_url = image_url

    def __repr__(self):
        return f"<Item: {self.title} [{self.type.upper()} | {self.status}]>"


# ─────────────────────────────────────────
#  Claim Model
# ─────────────────────────────────────────

class Claim:
    """Links a Student claimant to an Item, with a 48-hour reservation window."""
    VALID_STATUSES = ["pending", "approved", "rejected", "expired"]

    def __init__(
        self,
        id: str,
        item_id: str,
        claimant_id: str,
        status: str = "pending",
        proof_description: str = None,
        reserved_at: datetime = None,
        expires_at: datetime = None,
        resolved_by: str = None,
        resolved_at: datetime = None,
    ):
        assert status in self.VALID_STATUSES
        self.id = id
        self.item_id = item_id
        self.claimant_id = claimant_id
        self.status = status
        self.proof_description = proof_description
        self.reserved_at = reserved_at
        self.expires_at = expires_at
        self.resolved_by = resolved_by
        self.resolved_at = resolved_at

    def is_expired(self) -> bool:
        if self.expires_at and self.status == "pending":
            return datetime.utcnow() > self.expires_at
        return False


# ─────────────────────────────────────────
#  Audit Log Model
# ─────────────────────────────────────────

class AuditLog:
    """Records who did what, to which resource, and when."""
    def __init__(
        self,
        id: str,
        actor_id: str,
        action: str,
        target_type: str,
        target_id: str = None,
        details: dict = None,
        created_at: datetime = None,
    ):
        self.id = id
        self.actor_id = actor_id
        self.action = action
        self.target_type = target_type
        self.target_id = target_id
        self.details = details or {}
        self.created_at = created_at or datetime.utcnow()

    def __repr__(self):
        return f"<AuditLog: {self.action} on {self.target_type} by {self.actor_id}>"


# ─────────────────────────────────────────
#  Pydantic Schemas (for API request/response)
# ─────────────────────────────────────────

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: Literal["student", "faculty"]
    student_id: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ItemCreateRequest(BaseModel):
    type: Literal["lost", "found"]
    title: str
    category: str
    description: Optional[str] = None
    brand: Optional[str] = None
    color: Optional[str] = None
    location_found: Optional[str] = None
    image_url: Optional[str] = None


class ClaimCreateRequest(BaseModel):
    item_id: str
    proof_description: Optional[str] = None
    proof_image_url: Optional[str] = None
