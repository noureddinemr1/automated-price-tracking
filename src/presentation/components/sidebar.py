import streamlit as st
import asyncio
from src.services.product_service import ProductService
from src.services.price_service import PriceService
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import time

class Sidebar:
    def __init__(self, product_service: ProductService,price_service :PriceService):
        self.product_service = product_service
        self.price_service=price_service
        

    def render(self):
        if 'scheduler' not in st.session_state:
            st.session_state.scheduler = BackgroundScheduler()
            st.session_state.scheduler.start()
            st.session_state.job_id = None

        st.sidebar.header("Add New Product")
        new_url = st.sidebar.text_input("Product URL")
        prompt = st.sidebar.text_input(
            "AI Prompt (optional)",
            help="Provide AI-driven scraping guidance for Firecrawl API",
        )

        if st.sidebar.button("Add Product") and new_url:
            success, message = asyncio.run(
                self.product_service.add_product(new_url,prompt)  # Pass the prompt
            )
            if success:
                st.sidebar.success(message)
                st.rerun()
            else:
                st.sidebar.error(message)

        frequency_days = st.sidebar.number_input("Select scraping frequency (in days):", min_value=1, value=4, step=1)
        if st.sidebar.button("Schedule Scraping Job"):
            # If a job is already scheduled, remove it.
            if st.session_state.job_id:
                try:
                    st.session_state.scheduler.remove_job(st.session_state.job_id)
                except Exception as e:
                    st.sidebar.write("Error removing previous job:", e)

            job = st.session_state.scheduler.add_job(
                self.price_service.check_prices,
                trigger="interval",
                days=frequency_days,
                # Set next_run_time to a few seconds from now to verify it works
                next_run_time=datetime.now() + timedelta(seconds=5),
                id=f"scrape_job",
            )
            st.session_state.job_id = job.id
            st.sidebar.write(f"Scraping job scheduled to run every {frequency_days} day(s).")
        if st.session_state.job_id:
            job = st.session_state.scheduler.get_job(st.session_state.job_id)
            st.sidebar.write("Next run time:", job.next_run_time)