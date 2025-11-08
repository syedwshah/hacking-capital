import streamlit as st
from ui.api_client import get_health

st.title("Dashboard")
st.write("API health:")
try:
    health = get_health()
    st.success(health)
except Exception as e:
    st.error(f"API not reachable: {e}")


