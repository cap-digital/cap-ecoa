from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from ..database import Base


class AlertType(str, enum.Enum):
    NEWS_MATCH = "news_match"
    SENTIMENT_ALERT = "sentiment_alert"
    TRENDING = "trending"


class Alert(Base):
    __tablename__ = "ecoa_alerts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("ecoa_users.id", ondelete="CASCADE"), nullable=False, index=True)
    term_id = Column(String(36), ForeignKey("ecoa_monitored_terms.id", ondelete="SET NULL"), nullable=True, index=True)
    news_id = Column(String(36), ForeignKey("ecoa_news.id", ondelete="SET NULL"), nullable=True, index=True)
    alert_type = Column(Enum(AlertType), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    message = Column(Text, nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="alerts")
    term = relationship("MonitoredTerm", back_populates="alerts")
    news = relationship("News", back_populates="alerts")

    # Indexes
    __table_args__ = (
        Index('idx_alert_user_read', 'user_id', 'is_read'),
        Index('idx_alert_created', 'created_at'),
    )

    def __repr__(self):
        return f"<Alert {self.title[:30]}...>"
