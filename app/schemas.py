from pydantic import BaseModel, HttpUrl, EmailStr, Field
from enum import Enum
from typing import Optional, Dict
from uuid import UUID

# --- Enums (from project specs) ---

class NotificationType(str, Enum):
    email = "email"
    push = "push"

class NotificationStatus(str, Enum):
    delivered = "delivered"
    pending = "pending"
    failed = "failed"

# --- Request Models (from project specs) ---

class UserData(BaseModel):
    name: str
    link: HttpUrl
    meta: Optional[Dict] = None

class NotificationRequest(BaseModel):
    notification_type: NotificationType
    user_id: UUID
    template_code: str
    variables: UserData
    request_id: str
    priority: int
    metadata: Optional[Dict] = None

# --- Status Update Model (from project specs) ---

class StatusUpdateRequest(BaseModel):
    notification_id: str
    status: NotificationStatus
    timestamp: str  # We'll use ISO timestamps
    error: Optional[str] = None