import streamlit as st
import asyncio
from src.services.product_service import ProductService


class Sidebar:
    def __init__(self, product_service: ProductService):
        self.product_service = product_service

    def render(self):
        st.sidebar.header("Add New Product")
        new_url = st.sidebar.text_input("Product URL")
        prompt = st.sidebar.text_input(
            "AI Prompt (optional)",
            help="Provide AI-driven scraping guidance for Firecrawl API",
        )

        if st.sidebar.button("Add Product") and new_url:
            success, message = asyncio.run(
                self.product_service.add_product(new_url, prompt=prompt)
            )
            if success:
                st.sidebar.success(message)
                st.rerun()
            else:
                st.sidebar.error(message)