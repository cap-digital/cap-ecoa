from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from ..database import Base


class MonitoredTerm(Base):
    __tablename__ = "ecoa_monitored_terms"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("ecoa_users.id", ondelete="CASCADE"), nullable=False, index=True)
    term = Column(String(255), nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="monitored_terms")
    news_matches = relationship("NewsTermMatch", back_populates="term", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="term", cascade="all, delete-orphan")

    # Unique constraint
    __table_args__ = (
        UniqueConstraint('user_id', 'term', name='uq_user_term'),
        Index('idx_term_user_active', 'user_id', 'is_active'),
    )

    def __repr__(self):
        return f"<MonitoredTerm {self.term}>"


class NewsTermMatch(Base):
    __tablename__ = "ecoa_news_term_matches"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    news_id = Column(String(36), ForeignKey("ecoa_news.id", ondelete="CASCADE"), nullable=False, index=True)
    term_id = Column(String(36), ForeignKey("ecoa_monitored_terms.id", ondelete="CASCADE"), nullable=False, index=True)
    match_count = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    news = relationship("News", back_populates="term_matches")
    term = relationship("MonitoredTerm", back_populates="news_matches")

    # Unique constraint
    __table_args__ = (
        UniqueConstraint('news_id', 'term_id', name='uq_news_term'),
    )

    def __repr__(self):
        return f"<NewsTermMatch news={self.news_id} term={self.term_id}>"
