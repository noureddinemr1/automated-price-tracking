from typing import List
from datetime import datetime
from firecrawl import FirecrawlApp

from infrastructure.repositories.product_repository import ProductRepository
from domain.models import Product, PriceHistoryCreate
from services.notifications import send_price_alert
from config import settings


class PriceService:
    def __init__(self, product_repository: ProductRepository):
        self.repository = product_repository
        self.firecrawl = FirecrawlApp()

    async def check_prices(self) -> List[Product]:
        """Check prices for all tracked products and send alerts if needed"""
        products = self.repository.get_all()
        updated_products = []

        for product in products:
            try:
                # Get latest price
                scraped_data = await self.firecrawl.scrape_url(product.url)
                new_price = scraped_data["extract"]["price"]

                # Get earliest price from history
                price_history = self.repository.get_price_history(product.url)
                if price_history:
                    oldest_price = price_history[0].price  # Compare with first (oldest) price
                    if oldest_price > new_price:
                        drop_pct = (oldest_price - new_price) / oldest_price

                        if drop_pct >= settings.PRICE_DROP_THRESHOLD:
                            await send_price_alert(
                                product.name,
                                oldest_price,
                                new_price,
                                product.url,
                            )

                # Save new price history BEFORE updating product
                price_history = PriceHistoryCreate(
                    product_url=product.url,
                    price=new_price,
                    product_name=product.name,
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
