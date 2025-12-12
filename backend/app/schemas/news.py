from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class SentimentType(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class NewsSource(str, Enum):
    G1 = "g1"
    CNN = "cnn"
    TWITTER = "twitter"
    THREADS = "threads"


class NewsBase(BaseModel):
    title: str
    summary: Optional[str] = None
    content: Optional[str] = None
    url: str
    image_url: Optional[str] = None
    author: Optional[str] = None
    source: NewsSource
    published_at: Optional[datetime] = None


class NewsCreate(NewsBase):
    pass


class NewsResponse(NewsBase):
    id: str
    sentiment: Optional[SentimentType] = None
    sentiment_score: Optional[float] = None
    scraped_at: datetime
    matched_terms: List[str] = []

    class Config:
        from_attributes = True


class NewsListResponse(BaseModel):
    items: List[NewsResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class NewsFilters(BaseModel):
    term: Optional[str] = None
    source: Optional[NewsSource] = None
    sentiment: Optional[SentimentType] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    page: int = 1
    per_page: int = 20
