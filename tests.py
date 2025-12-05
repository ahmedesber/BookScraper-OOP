import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import BookData, DatabaseManager, Base, BookModel

# 1. UNIT TEST: Data Class
def test_book_data_structure():
    """Test that the data class correctly holds information."""
    book = BookData(title="Test", price=10.0, availability="Yes", rating="Five")
    assert book.title == "Test"
    assert book.price == 10.0

# 2. INTEGRATION TEST: Database
def test_database_save():
    """Test saving data to an in-memory database."""
    # Create in-memory DB
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    
    # Setup Manager with test engine
    manager = DatabaseManager("sqlite:///:memory:")
    manager.engine = engine
    manager.Session = sessionmaker(bind=engine)
    
    # Create Mock Data
    mock_books = [BookData("Test Book", 50.0, "In Stock", "One")]
    
    # Action
    manager.save_books(mock_books)
    
    # Assert
    session = manager.Session()
    result = session.query(BookModel).first()
    assert result.title == "Test Book"
    session.close()