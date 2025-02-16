#price_service
from typing import List
from firecrawl import FirecrawlApp

from src.config import settings
from src.domain.models import Product, ProductCreate, PriceHistoryCreate
from src.infrastructure.repositories.product_repository import ProductRepository
from src.services.notifications import send_price_alert
import os
from dotenv import load_dotenv

load_dotenv()


class PriceService:
    def __init__(self, product_repository: ProductRepository):
        self.repository = product_repository
        self.firecrawl = FirecrawlApp(api_key=os.getenv('FIRECRAWL_API_KEY'))

async def check_prices(self) -> List[Product]:
    """Check prices for all tracked products and send alerts if needed"""
    products = self.repository.get_all()
    updated_products = []

    for product in products:
        try:
            # Get latest price
            scraped_data = self.firecrawl.scrape_url(product.url, params=params) # type: ignore
            new_price = float(scraped_data["extract"]["price"])
            if not new_price : new_price = float(scraped_data["metadata"]["price"])
            cabin_type = scraped_data["extract"].get("cabin_type")  # Extract cabin type from Firecrawl response

            # Get all price history for the product
            price_history = self.repository.get_price_history(product.url)

            # Find the lowest price across all cabin types
            lowest_price = min([ph.price for ph in price_history], default=new_price)

            # Save new price history
            price_history = PriceHistoryCreate(
                product_url=product.url,
                price=new_price,
                product_name=product.name,
                cabin_type=cabin_type,
                is_lowest=(new_price <= lowest_price),  # Mark as lowest if applicable
            )
            self.repository.add_price_history(price_history)

            # Update product price in database
            product.price = new_price
            self.repository.update(product)

            updated_products.append(product)

        except Exception as e:
            print(f"Error checking price for {product.url}: {e}")
            continue

    return updated_products