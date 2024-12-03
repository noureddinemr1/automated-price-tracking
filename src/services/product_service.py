from typing import Tuple, Optional
from urllib.parse import urlparse
from datetime import datetime
from firecrawl import FirecrawlApp

from infrastructure.repositories.product_repository import ProductRepository
from domain.models import ProductCreate, PriceHistoryCreate, Product
from services.notifications import send_price_alert
from config import settings


class ProductService:
    def __init__(self, product_repository: ProductRepository):
        self.repository = product_repository
        self.firecrawl = FirecrawlApp()

    async def add_product(self, url: str) -> Tuple[bool, str]:
        """Add a new product to track"""
        if not self._validate_url(url):
            return False, "Please enter a valid URL"

        try:
            normalized_url = self._normalize_amazon_url(url)
            print(f"Normalized URL: {normalized_url}")
            if not normalized_url:
                return False, "Invalid Amazon product URL"

            # Check if product exists
            existing_product = self.repository.get(normalized_url)
            print(f"Existing product: {existing_product}")
            if existing_product:
                return False, "Product already being tracked!"

            # Scrape product
            scraped_product = await self._scrape_product(url, normalized_url)
            print(f"Scraped product: {scraped_product}")

            # Create product
            product = self.repository.add(scraped_product)
            print(f"Added product: {product}")

            # Add initial price history
            price_history = PriceHistoryCreate(
                product_url=product.url, price=product.price, product_name=product.name
            )
            self.repository.add_price_history(price_history)

            return (
                True,
                f"Added and checked initial price for: {product.name} - ${product.price:.2f}",
            )

        except Exception as e:
            print(f"Error: {str(e)}")
            return False, f"Error adding product: {str(e)}"

    def _validate_url(self, url: str) -> bool:
        """Validate URL format"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

    def _normalize_amazon_url(self, url: str) -> Optional[str]:
        """Normalize Amazon URL to consistent format"""
        try:
            if "/dp/" in url:
                asin = url.split("/dp/")[1].split("/")[0]
            elif "/gp/product/" in url:
                asin = url.split("/gp/product/")[1].split("/")[0]
            elif "/gp/aw/d/" in url:
                asin = url.split("/gp/aw/d/")[1].split("/")[0]
            else:
                return None
            return f"https://www.amazon.com/dp/{asin}"
        except Exception:
            return None

    async def _scrape_product(self, url: str, normalized_url: str) -> ProductCreate:
        """Scrape product details"""
        data = self.firecrawl.scrape_url(
            url,
            params={
                "formats": ["extract"],
                "extract": {"schema": ProductCreate.model_json_schema()},
            },
        )
        product_data = data["extract"]
        product_data["url"] = normalized_url
        return ProductCreate(**product_data)
