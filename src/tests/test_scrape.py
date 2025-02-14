import sys
import os
from firecrawl import FirecrawlApp
from dotenv import load_dotenv
import datetime


# Add the 'src' directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the ProductCreate schema from the domain.models module
from domain.models import ProductCreate, PriceHistoryCreate

# Load environment variables
load_dotenv()

# Initialize the FirecrawlApp with your API key
api_key = os.getenv("FIRECRAWL_API_KEY")
if not api_key:
    raise ValueError("FIRECRAWL_API_KEY environment variable is not set.")

app = FirecrawlApp(api_key=api_key)

# URL of the product to scrape
url = "https://megapc.tn/shop/product/MSI-GeForce-GTX-1660-Ti-ARMOR-6GB-OC"

data = app.scrape_url(
            url,
            params={
                "formats": ["extract"],
                "extract": {"schema": ProductCreate.model_json_schema()},
            },
        )
product_data = {}

 # Use original URL
extract = data["extract"]
product_data["url"] = url

# Iterate through the metadata to find the price
for key, value in extract.items():
    if "name" in key.lower() or "title" in key.lower():
        product_data["name"] = value
    if "price" in key.lower():
        product_data["price"] = value
    if "currency" in key.lower():
        product_data["currency"] = value
    if "image" in key.lower():
        product_data["main_image_url"] = value

#get system date now
print(product_data)