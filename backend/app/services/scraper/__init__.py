# Scraper package
from .base import BaseScraper
from .g1 import G1Scraper
from .cnn import CNNScraper

__all__ = ["BaseScraper", "G1Scraper", "CNNScraper"]
