from firecrawl import FirecrawlApp
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize the FirecrawlApp with your API key
api_key = os.getenv("FIRECRAWL_API_KEY")
app = FirecrawlApp(api_key=api_key)

# URL of the product to scrape
mytek_product = "https://www.mytek.tn/pc-portable-lenovo-ideapad-slim-3-15iru8-i3-13e-gen-8g-256g-ssd-gris.html"

# Scrape the product page
data = app.scrape_url(mytek_product)

# Print the entire scraped data for inspection

# Extract the price and currency from metadata
product = data.get("metadata", {})
price = product.get("product:price:amount")
currency = product.get("product:price:currency")

# Print the results
if price and currency:
    print(f"Price: {price} {currency}")
else:
    print("Price or currency not found in the scraped data.")