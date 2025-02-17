import pandas as pd
import streamlit as st
from sqlalchemy import desc

from src.services.product_service import ProductService
from src.services.price_service import PriceService
from .price_chart import PriceChart


class ProductList:
    def __init__(self, product_service: ProductService,priceService :PriceService):
        self.product_service = product_service
        self.priceService=priceService
        self.price_chart = PriceChart()

    def render(self, products):
        for product in products:
            with st.container():
                st.markdown(f"#### {product.name}")
                col1, col2, col3 = st.columns([1, 3, 3])    
                # Display product image
                try:
                    col1.image(product.main_image_url, use_container_width=True)
                except Exception as e:
                    col1.error("Image could not be loaded for this product.")

                # Get price history
                price_history = self.product_service.repository.get_price_history(
                    product.url
                )

                if price_history:
                    # Convert to DataFrame for plotting
                    df = pd.DataFrame(
                        [
                            {"timestamp": ph.timestamp, "price": ph.price}
                            for ph in price_history
                        ]
                    )

                    # Find the lowest price and cabin type
                    lowest_price = df["price"].min()
                    cabin_type = price_history[-1].cabin_type if hasattr(price_history[-1], "cabin_type") else "N/A"

                    # Create and display chart
                    fig = self.price_chart.create(df, cabin_type=cabin_type)
                    col2.plotly_chart(fig, use_container_width=True)

                    # Show current price and lowest price
                    latest_price = price_history[-1].price
                    col3.metric("Current Price", f"${latest_price:.2f}", delta=None)
                    col3.metric("Lowest Price", f"${lowest_price:.2f}", delta=None)
                else:
                    col2.info("No price history available")

                # Add visit product button
                col3.link_button("Visit Product", product.url)
                
                if col3.button("Scrape now",key=f"scrape_{product.url}"):
                    self.priceService.update_price(product)
                col3.download_button(
                        label="Download History as CSV",
                        data=self.product_service.get_csv_file(product.url),
                        file_name=f"{product.name}_history.csv",
                        mime="text/csv",)

                

                if st.button("Remove from tracking", key=f"remove_{product.url}"):
                    self.product_service.remove_product(product.url)
                    st.success("Product removed from tracking!")
                    st.rerun()
            st.markdown("--------")