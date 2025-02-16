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
app = 
# Initialize the FirecrawlApp with your API key
api_key = os.getenv("FIRECRAWL_API_KEY")
def fn() : 
      
    params = {
            "formats": ["extract"],
            "extract": {"schema": ProductCreate.model_json_schema()},
            "pageOptions" : {
                "onlyMainContent" : True
            }
        }
    data = .scrape_url(url, params=params)
    product_data = {}

        # Use original URL
    product_data["url"] = url

        # Check both 'extract' and 'metadata' fields
    extract = data.get("extract", {})
    metadata = data.get("metadata", {})

        # Merge extract and metadata, prioritizing extract
    merged_data = {**extract, **metadata}

        # Extract product details using a generalized approach
    product_data.update(self._extract_product_details(merged_data))

        # Add the check date
    product_data["check_date"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    print(product_data)


fn()