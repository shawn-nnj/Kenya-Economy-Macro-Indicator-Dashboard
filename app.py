import streamlit as st

from shared import apply_theme, install_fullscreen

st.set_page_config(page_title="Kenya economy dashboard",
                   page_icon="kuramo_icon.jpg",      # keep whatever icon line you already had
                   layout="wide",
                   initial_sidebar_state="expanded")

apply_theme()
install_fullscreen()

pages = [
    st.Page("views/growth_drivers.py", title="Growth drivers",
            icon=":material/trending_up:", default=True),
    st.Page("views/sector_analysis.py", title="Sector analysis",
            icon=":material/pie_chart:"),
    st.Page("views/macro_indicators.py", title="Macro indicators",
            icon=":material/monitoring:"),
]

st.navigation(pages, position="top").run()
