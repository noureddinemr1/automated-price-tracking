import os
import sys

# Add the src directory to the Python path
src_path = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, src_path)

# Import and run the Streamlit app
from src.presentation.app import main

if __name__ == "__main__":
    main()
