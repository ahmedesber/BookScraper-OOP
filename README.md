# BooksToScrape - Python OOP Scraper

## Project Overview
This project is an advanced web scraper built to extract pricing and rating data from `books.toscrape.com`. It demonstrates the use of **Object-Oriented Programming**, **modern scraping libraries**, and **ORM database management**.

### Core Technologies
* **Scraping:** `Playwright` (Async/Await)
* **Database:** `SQLite` via `SQLAlchemy` ORM
* **Architecture:** Abstract Base Classes, Data Classes, and Dependency Injection.

## Setup & Installation

1.  **Clone the Repository**
    ```bash
    git clone <your_repo_link>
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    playwright install chromium
    ```

## Usage

**Run the Scraper:**
```bash
python main.py