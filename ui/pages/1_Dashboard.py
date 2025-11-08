import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui.api_client import get_health

st.title("Dashboard")
st.write("API health:")
try:
    health = get_health()
    st.success(health)
except Exception as e:
    st.error(f"API not reachable: {e}")


