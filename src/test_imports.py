from infrastructure.repositories.product_repository import ProductRepository
from infrastructure.database import Product, PriceHistory, SessionLocal

# Create a session
session = SessionLocal()

# Create repository
repo = ProductRepository(session)

try:
    # Test getting all products
    products = repo.get_all()
    print(f"Found {len(products)} products")
    print("Imports and basic functionality working correctly!")
finally:
    session.close()
