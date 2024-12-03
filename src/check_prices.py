import asyncio
from services.price_service import PriceService
from infrastructure.repositories.product_repository import ProductRepository
from infrastructure.database import get_session


async def main():
    session = next(get_session())
    repository = ProductRepository(session)
    price_service = PriceService(repository)
    try:
        updated_products = await price_service.check_prices()
        print(f"Successfully checked prices for {len(updated_products)} products")
    except Exception as e:
        print(f"Error checking prices: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    asyncio.run(main())
