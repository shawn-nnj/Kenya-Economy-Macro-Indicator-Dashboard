import streamlit as st

from shared import apply_theme, install_fullscreen

st.set_page_config(page_title="Kenya Economy Dashboard",
                   page_icon=":material/trending_up:",
                   layout="wide",
                   initial_sidebar_state="expanded")

apply_theme()
install_fullscreen()

pages = [
    st.Page("views/growth_drivers.py", title="Growth drivers",
            icon=":material/trending_up:", default=True),
    st.Page("views/sector_analysis.py", title="Sector analysis",
            icon=":material/pie_chart:"),
]

st.navigation(pages, position="top").run()