import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import desc
from services.product_service import ProductService
from presentation.components.price_chart import PriceChart


class ProductList:
    def __init__(self, product_service: ProductService):
        self.product_service = product_service
        self.price_chart = PriceChart()

    def render(self, products):
        for product in products:
            with st.expander(f"{product.name}", expanded=False):
                col1, col2, col3 = st.columns([3, 1, 1])

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

                    # Create and display chart
                    fig = self.price_chart.create(df)
                    col1.plotly_chart(fig, use_container_width=True)

                    # Show current price
                    latest_price = price_history[-1].price
                    col2.metric("Current Price", f"${latest_price:.2f}", delta=None)
                else:
                    col1.info("No price history available")

                # Add visit product button
                col3.link_button("Visit Product", product.url)

                if st.button("Remove from tracking", key=f"remove_{product.url}"):
                    self.product_service.remove_product(product.url)
                    st.success("Product removed from tracking!")
                    st.rerun()
