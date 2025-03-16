from typing import Tuple, Optional, Dict, Any
from datetime import datetime
from urllib.parse import urlparse
import re
from dotenv import load_dotenv
from firecrawl import FirecrawlApp
from src.domain.models import ProductCreate, PriceHistoryCreate
from src.infrastructure.repositories.product_repository import ProductRepository
import os
import pandas as pd


load_dotenv()


class ProductService:
    def __init__(self, product_repository: ProductRepository):
        self.repository = product_repository
        self.firecrawl = FirecrawlApp(api_key=os.getenv('FIRECRAWL_API_KEY'))

    def _validate_url(self, url: str) -> bool:
        """Validate URL format"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])  # Ensure URL has a scheme and netloc
        except ValueError:
            return False
        



    def get_csv_file(self ,product_url : str ):
        return self.repository.get_csv_prices(product_url)

    async def add_product(self, url: str, prompt: str = None) -> Tuple[bool, str]:
        """Add a new product to track"""
        if not self._validate_url(url):
            return False, "Please enter a valid URL"

        try:
            # Check if product exists
            existing_product = self.repository.get(url)

            if existing_product:
                return False, "Product already being tracked!"

            # Scrape product
            scraped_product = await self._scrape_product(url, prompt)

            # Create product
            product = self.repository.add(scraped_product)

            # Add initial price history
            price_history = PriceHistoryCreate(
                product_url=product.url, price=product.price, product_name=product.name
            )
            self.repository.add_price_history(price_history)

            return (
                True,
                f"Added and checked initial price for: {product.name} - {product.currency} {product.price:.2f}",
            )

        except Exception as e:
            print(f"Error: {str(e)}")
            return False, f"Error adding product: {str(e)}"

    async def _scrape_product(self, url: str, prompt: str ) -> ProductCreate:
        """Scrape product details from any e-commerce website"""

        params = {
            'prompt': prompt,
            'schema': ProductCreate.model_json_schema(),
        }

        data = self.firecrawl.extract([url],params)
        product_data = data["data"]



        # Extract product details using a generalized approach
        product_data.update(self._extract_product_details(product_data))

        # Add the check date
        product_data["check_date"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        # Include the prompt field in the ProductCreate model
        product_data["prompt"] = prompt


        return ProductCreate(**product_data)

    def _extract_product_details(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract product details from a dictionary using a generalized approach"""
        product_data = {}

        # Helper function to find a value by key pattern
        def find_value_by_pattern(patterns, default=None):
            for pattern in patterns:
                for key, value in data.items():
                    if re.search(pattern, key, re.IGNORECASE):
                        return value
            return default

        # Extract product name
        product_data["name"] = find_value_by_pattern(
            ["name", "title", "product"], default="Unknown Product"
        )

        # Extract product price
        price = find_value_by_pattern(["price", "amount", "cost"])
        if price:
            try:
                # Remove currency symbols and commas, then convert to float
                price = float(re.sub(r"[^\d.]", "", str(price)))
                product_data["price"] = price
            except (ValueError, TypeError):
                print(f"Warning: Invalid price value '{price}'. Skipping.")

        # Extract currency
        currency = find_value_by_pattern(["currency", "curr", "symbol"])
        if currency:
            # Normalize currency to a 3-letter code (e.g., USD, EUR)
            currency = self._normalize_currency(currency)
        product_data["currency"] = currency or "USD"  # Default to USD

        # Extract main image URL
        product_data["main_image_url"] = find_value_by_pattern(
            ["image", "img", "photo", "picture"], default=""
        )

        return product_data

    def _normalize_currency(self, currency: str) -> str:
        """Normalize currency to a 3-letter code (e.g., USD, EUR)"""
        currency = currency.upper()
        # Map common currency symbols to codes
        currency_map = {
            "$": "USD",
            "€": "EUR",
            "£": "GBP",
            "¥": "JPY",
            "₹": "INR",
            "TND": "TND",  # Add more mappings as needed
        }
        return currency_map.get(currency, currency)

    def remove_product(self, url: str) -> None:
        """Remove a product and its price history"""
        product = self.repository.get(url)
        if product:
            self.repository.delete(url)