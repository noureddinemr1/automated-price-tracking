import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()


class Product(Base):
    __tablename__ = "products"

    url = Column(String, primary_key=True)
    name = Column(String)
    price = Column(Float)
    currency = Column(String)
    check_date = Column(String)
    main_image_url = Column(String)


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True)
    product_url = Column(String, index=True)
    price = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    product_name = Column(String)


def get_db_url():
    """Get database URL with fallback to SQLite for local development"""
    db_url = os.getenv("POSTGRES_URL")
    if db_url:
        # Fix Supabase connection string if needed
        result = urlparse(db_url)
        if result.scheme == "postgres":
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        print(f"Using PostgreSQL: {db_url}")
    else:
        # Fallback for local development
        db_url = "sqlite:///data/price_history.db"
    return db_url


engine = create_engine(
    get_db_url(),
    pool_pre_ping=True,  # Helps prevent disconnection errors
    pool_size=5,
    max_overflow=10,
)
Session = sessionmaker(bind=engine)

# Create tables if they don't exist
Base.metadata.create_all(engine)


def change_product_price(product_url: str, new_price: float):
    session = Session()
    session.query(PriceHistory).filter(PriceHistory.product_url == product_url).update(
        {"price": new_price}
    )

    session.commit()


def print_price_history():
    session = Session()
    records = session.query(PriceHistory).all()

    for record in records:
        print(f"Product Name: {record.product_name}")
        print(f"Product URL: {record.product_url}")
        print(f"Price: ${record.price:.2f}")
        print(f"Timestamp: {record.timestamp}")
        print("-" * 80)


if __name__ == "__main__":
    # change_product_price(
    #     "https://www.amazon.com/dp/B09HMV6K1W",
    #     1000.99,
    # )

    print_price_history()
