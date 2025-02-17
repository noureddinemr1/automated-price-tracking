#price_service
from typing import List
from firecrawl import FirecrawlApp

from src.config import settings
from src.domain.models import Product, ProductCreate, PriceHistoryCreate,PriceHistory
from src.infrastructure.repositories.product_repository import ProductRepository
import os
import asyncio

from dotenv import load_dotenv
import time
from src.services.notifications import send_price_error,send_price_alert
load_dotenv()


class PriceService:
    def __init__(self, product_repository: ProductRepository):
        self.repository = product_repository
        self.firecrawl = FirecrawlApp(api_key=os.getenv('FIRECRAWL_API_KEY'))


        
    def update_price(self,product : Product )-> Product :
            # Get latest price
            params = {
            "formats": ["extract"],
            "extract": {
                "schema": ProductCreate.model_json_schema(),
            }
        }
            
            scraped_data = self.firecrawl.scrape_url(product.url, params=params) # type: ignore
            try :
                new_price = float(scraped_data["extract"]["price"])
                if not new_price : new_price = float(scraped_data["metadata"]["price"])
            except Exception as e:
                 asyncio.run(send_price_error(product.name,product.url,f"No price Found : {e}"))
                 new_price=product.price
            cabin_type = scraped_data["extract"].get("cabin_type")  # Extract cabin type from Firecrawl response
            if product.price<new_price:
                 asyncio.run(send_price_alert(product.name,product.price,new_price,product.url)) 
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
            return product

            

    def check_prices(self) -> List[Product]:
        """Check prices for all tracked products and send alerts if needed"""
        products = self.repository.get_all()
        updated_products = []

        for product in products:
            try:
                # Get latest price
                
                updated_product= self.update_price(product)
                updated_products.append(updated_product)
                # make a buffer between each request to deal with rate limiter
                time.sleep(10)
            except Exception as e:
                asyncio.run(send_price_error(product.name,product.url,e))
                print(f"Error checking price for {product.url}: {e}")
                continue

        return updated_products