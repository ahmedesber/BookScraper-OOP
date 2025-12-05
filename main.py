"""
BookScraper Project
Extracts book data from books.toscrape.com and saves it to a SQLite database.
"""

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

# Database Imports
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

# Scraping Imports
from playwright.async_api import async_playwright

# 1. DATA MODELS
# ========================================================
Base = declarative_base()

@dataclass
class BookData:
    """Data Transfer Object for Book information."""
    title: str
    price: float
    availability: str
    rating: str

class BookModel(Base):
    """SQLAlchemy ORM Model for the 'books' table."""
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    price = Column(Float)
    availability = Column(String)
    rating = Column(String)

    def __repr__(self):
        return f"<Book(title='{self.title}', price={self.price})>"

# 2. ABSTRACT BASE CLASS (OOP Requirement)
# ========================================================
class BaseScraper(ABC):
    """Abstract interface for all scrapers."""

    def __init__(self, base_url: str):
        self.base_url = base_url

    @abstractmethod
    async def fetch_data(self) -> List[BookData]:
        """Scrapes data from the source."""

# 3. CONCRETE IMPLEMENTATION (Playwright)
# ========================================================
class BookScraper(BaseScraper):
    """Concrete scraper for books.toscrape.com using Playwright."""

    async def fetch_data(self) -> List[BookData]:
        print(f"Starting scrape on {self.base_url}...")
        results = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(self.base_url)

            # Wait for books to load
            await page.wait_for_selector(".product_pod")
            books = await page.query_selector_all(".product_pod")

            for book in books:
                # Extract Title
                title_el = await book.query_selector("h3 a")
                title = await title_el.get_attribute("title")

                # Extract Price
                price_el = await book.query_selector(".price_color")
                price_text = await price_el.inner_text()
                price = float(price_text.replace("£", ""))

                # Extract Availability
                avail_el = await book.query_selector(".instock.availability")
                avail = (await avail_el.inner_text()).strip()

                # Extract Rating
                rating_el = await book.query_selector(".star-rating")
                rating_class = await rating_el.get_attribute("class")
                rating = rating_class.replace("star-rating ", "")

                book_obj = BookData(title, price, avail, rating)
                results.append(book_obj)
                print(f"Scraped: {title}")

            await browser.close()
        return results

# 4. DATABASE MANAGER
# ========================================================
class DatabaseManager:
    """Handles all database interactions."""

    def __init__(self, connection_string: str):
        self.engine = create_engine(connection_string)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def save_books(self, books: List[BookData]):
        """Saves a list of BookData objects to the database."""
        session = self.Session()
        try:
            for b in books:
                record = BookModel(
                    title=b.title,
                    price=b.price,
                    availability=b.availability,
                    rating=b.rating
                )
                session.add(record)
            session.commit()
            print(f"Successfully saved {len(books)} books.")
        except Exception as e: # pylint: disable=broad-except
            print(f"Error saving to DB: {e}")
            session.rollback()
        finally:
            session.close()

# 5. MAIN EXECUTION
# ========================================================
async def main():
    """Main entry point."""
    TARGET_URL = "http://books.toscrape.com/"
    DB_CONNECTION = "sqlite:///books.db"

    scraper = BookScraper(TARGET_URL)
    db_manager = DatabaseManager(DB_CONNECTION)

    data = await scraper.fetch_data()
    
    if data:
        db_manager.save_books(data)
    else:
        print("No data found.")

if __name__ == "__main__":
    asyncio.run(main())