from sqlalchemy import Column, String, DateTime, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from ..database import Base


class PlanType(str, enum.Enum):
    FREE = "free"
    PRO = "pro"


class User(Base):
    __tablename__ = "ecoa_users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    political_name = Column(String(255), nullable=True)
    party = Column(String(100), nullable=True)
    state = Column(String(2), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    plan_type = Column(Enum(PlanType), default=PlanType.FREE)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    monitored_terms = relationship("MonitoredTerm", back_populates="user", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email}>"
