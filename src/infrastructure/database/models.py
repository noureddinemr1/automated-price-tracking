import os
from sqlalchemy import Boolean, create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
from urllib.parse import urlparse

Base = declarative_base()



class Product(Base):
    __tablename__ = "products"

    url = Column(String, primary_key=True)
    name = Column(String)
    price = Column(Float)
    currency = Column(String)
    check_date = Column(String)
    main_image_url = Column(String)
    prompt = Column(String, nullable=True)  # New field


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True)
    product_url = Column(String, index=True)
    price = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    product_name = Column(String)
    cabin_type = Column(String)  # New column
    is_lowest = Column(Boolean, default=False)  # New column