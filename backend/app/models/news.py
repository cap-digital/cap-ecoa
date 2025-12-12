from sqlalchemy import Column, String, Text, DateTime, Enum, Float, Boolean, Index
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from ..database import Base


class SentimentType(str, enum.Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class NewsSource(Base):
    __tablename__ = "ecoa_news_sources"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    slug = Column(String(50), unique=True, nullable=False)
    base_url = Column(String(255), nullable=False)
    scraper_type = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)
    last_scraped_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<NewsSource {self.name}>"


class News(Base):
    __tablename__ = "ecoa_news"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source = Column(String(50), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    summary = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    url = Column(Text, nullable=False)
    url_hash = Column(String(64), unique=True, nullable=False, index=True)  # SHA256 hash of URL
    image_url = Column(Text, nullable=True)
    author = Column(String(255), nullable=True)
    published_at = Column(DateTime, nullable=True, index=True)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    sentiment = Column(Enum(SentimentType), nullable=True, index=True)
    sentiment_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    term_matches = relationship("NewsTermMatch", back_populates="news", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="news")

    # Indexes
    __table_args__ = (
        Index('idx_news_source_published', 'source', 'published_at'),
        Index('idx_news_sentiment', 'sentiment'),
    )

    def __repr__(self):
        return f"<News {self.title[:50]}...>"
