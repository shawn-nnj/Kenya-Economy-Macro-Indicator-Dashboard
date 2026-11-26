import hashlib
import re

import plotly.graph_objects as go
import streamlit as st

DISPLAY = {
    "Agriculture, forestry and fishing": "Agriculture, Forestry and Fishing",
    "Mining and quarrying": "Mining and Quarrying",
    "Manufacturing": "Manufacturing",
    "Electricity supply": "Electricity Supply",
    "Water supply; sewerage, waste management": "Water Supply; Sewerage, Waste Management",
    "Construction": "Construction",
    "Wholesale and retail trade; repairs": "Wholesale and Retail Trade; Repairs",
    "Transportation and storage": "Transportation and Storage",
    "Accommodation and food service activities": "Accommodation and Food Service Activities",
    "Information and communication": "Information and Communication",
    "Financial and insurance activities": "Financial and Insurance Activities",
    "Real estate": "Real Estate",
    "Professional, scientific and technical activities": "Professional, Scientific and Technical Activities",
    "Administrative and support service activities": "Administrative and Support Service Activities",
    "Public administration and defence": "Public Administration and Defence",
    "Education": "Education",
    "Human health and social work activities": "Human Health and Social Work Activities",
    "Arts, entertainment and recreation": "Arts, Entertainment and Recreation",
    "Other service activities": "Other Service Activities",
    "Activities of households as employers": "Activities of Households as Employers",
    "Taxes on products": "Taxes on Products",
    "Financial Intermediation Services Indirectly Measured (FISIM)": "Financial Intermediation Services Indirectly Measured (FISIM)",
}


def display_name(name):
    """Capitalised, full sector name (falls back to the raw name)."""
    key = str(name).rstrip("; ").strip()
    return DISPLAY.get(key, key)


def section(title, sub, finding=None, min_h=0):
    """Section heading, a one-to-two sentence overview, and an optional finding line."""
    st.session_state["_last_section"] = (title, sub, finding)   # used by the full-screen pop-up
    st.markdown(f"##### {title}")
    html = f'<div style="min-height:{min_h}px">'
    html += f'<div style="color:#5B6573;font-size:0.9rem;margin-bottom:6px">{sub}</div>'
    if finding:
        html += f'<div style="color:#222;font-weight:600;margin-bottom:4px">{finding}</div>'
    html += "</div>"
    st.markdown(html.replace("$", r"\$"), unsafe_allow_html=True)


def apply_theme():
    """Shared styling. Call once, in app.py."""
    st.markdown("""
<style>
/* full-screen button: right-aligned above each chart */
[class*="st-key-fs_"] { display: flex; justify-content: flex-end; }
[class*="st-key-fs_"] button { color: #1F4E79; font-weight: 600; }
/* soft blue highlight on the selected / hovered menu item */
[data-testid="stTopNavLink"][aria-current="page"],
[data-testid="stSidebarNavLink"][aria-current="page"] { background-color: #DCE8F4 !important; }
[data-testid="stTopNavLink"]:hover, [data-testid="stSidebarNavLink"]:hover { background-color: #E8F0F8 !important; }
/* dropdown lists wide enough for full sector names */
div[data-baseweb="popover"] { min-width: 440px !important; }
/* KPI cards: same height, long text wraps instead of being cut off */
[data-testid="stMetric"] { height: 140px !important; }
[data-testid="stMetricLabel"] *, [data-testid="stMetricDelta"] * {
    white-space: normal !important; overflow: visible !important; text-overflow: clip !important;
}
[class*="st-key-kpi_name"] [data-testid="stMetricValue"] * {
    font-size: 1.05rem !important; white-space: normal !important; line-height: 1.2 !important;
}
/* full-screen pop-up: nearly the whole window */
div[data-testid="stDialog"] div[role="dialog"] { width: 96vw; max-width: 96vw; }
</style>
""", unsafe_allow_html=True)


_FS_VERSION = 4        # bump this number whenever you change install_fullscreen below


def install_fullscreen():
    """Give every st.plotly_chart a permanent 'Full screen' button and hide the hover toolbar."""
    current = st.plotly_chart
    if getattr(current, "_fs_version", None) == _FS_VERSION:
        return
    original = getattr(current, "_original", current)         # the real Streamlit function

    def plotly_chart(fig, *args, **kwargs):
        kwargs["config"] = {**kwargs.get("config", {}), "displayModeBar": False}
        key = "fs_" + hashlib.md5(fig.to_json().encode()).hexdigest()[:12]
        ctx = st.session_state.get("_last_section")          # title, overview and finding of this chart
        _, btn = st.columns([3, 1])
        if btn.button("Full screen", key=key, icon=":material/fullscreen:", type="tertiary"):
            title, sub, finding = ctx if ctx else ("Chart", "", None)
            heading = re.sub(r":material/[a-z0-9_]+:\s*", "", title).strip() or "Chart"

            @st.dialog(heading, width="large")
            def _show():
                if sub:
                    st.caption(sub.replace("$", r"\$"))
                if finding:
                    st.markdown(f"**{finding}**".replace("$", r"\$"))
                big = go.Figure(fig)
                big.update_layout(height=700)
                original(big, **kwargs)
            _show()
        original(fig, *args, **kwargs)

    plotly_chart._fs_version = _FS_VERSION
    plotly_chart._original = original
    st.plotly_chart = plotly_chart 