from firecrawl import FirecrawlApp
from pydantic import BaseModel, Field
from typing import Any, Optional, List

app = FirecrawlApp(api_key='fc-b75c7ffc064941369610bec7c2227513')



class ExtractSchema(BaseModel):
    url: str
    name: str

data = app.extract([
  "https://megapc.tn/shop/product/EVENTS/HELLO%20WINTER/SQUIDE-GAME-A1-AMD-Ryzen-3-3200G-8GB-RAM-480-GB-SSD"
], {
    'prompt': 'add a comma in the nama field',
    'schema': ExtractSchema.model_json_schema(),
})
print(data)