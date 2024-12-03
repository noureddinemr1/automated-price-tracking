import streamlit as st
import os
import sys

# Add src to Python path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from infrastructure.database import get_session
from infrastructure.repositories.product_repository import ProductRepository
from services.product_service import ProductService
from services.price_service import PriceService
from presentation.components.sidebar import Sidebar
from presentation.components.product_list import ProductList


def init_services():
    """Initialize services with dependencies"""
    session = next(get_session())
    repository = ProductRepository(session)
    product_service = ProductService(repository)
    price_service = PriceService(repository)
    return product_service, price_service


def render_dashboard(product_service: ProductService, price_service: PriceService):
    st.title("Price Tracker Dashboard")

    # Render sidebar
    sidebar = Sidebar(product_service)
    sidebar.render()

    # Main content
    st.header("Tracked Products")
    products = product_service.repository.get_all()

    if not products:
        st.info("No products are being tracked. Add some using the sidebar!")
    else:
        product_list = ProductList(product_service)
        product_list.render(products)


def main():
    st.set_page_config(page_title="Price Tracker", page_icon="📊", layout="wide")

    # Initialize services
    product_service, price_service = init_services()

    # Render dashboard
    render_dashboard(product_service, price_service)


if __name__ == "__main__":
    main()
