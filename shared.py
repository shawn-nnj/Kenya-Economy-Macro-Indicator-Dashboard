import base64
import hashlib
import io

import numpy as np
import plotly.graph_objects as go
import streamlit as st
from PIL import Image, ImageChops

PAGE_BG = (243, 245, 248)          # the #F3F5F8 page colour


def section(title, sub, finding=None, min_h=0):
    """Section heading, a one-to-two sentence overview, and an optional finding line.
    min_h keeps side-by-side cards the same height so their charts line up."""
    st.markdown(f"##### {title}")
    html = f'<div style="min-height:{min_h}px">'
    html += f'<div style="color:#5B6573;font-size:0.9rem;margin-bottom:6px">{sub}</div>'
    if finding:
        html += f'<div style="color:#222;font-weight:600;margin-bottom:4px">{finding}</div>'
    html += "</div>"
    st.markdown(html.replace("$", r"\$"), unsafe_allow_html=True)


@st.cache_data
def _bg_uri(opacity):
    """Kuramo graphic blended onto the page colour at the given strength (0 to 1)."""
    img = Image.open("kuramo_graphic.png").convert("RGBA")
    white = Image.new("RGBA", img.size, (255, 255, 255, 255))
    rgb = np.asarray(Image.alpha_composite(white, img).convert("RGB"), dtype=float) / 255
    out = np.array(PAGE_BG, dtype=float) * (1 - (1 - rgb) * opacity)
    buf = io.BytesIO()
    Image.fromarray(out.clip(0, 255).astype("uint8")).save(buf, "JPEG", quality=90)
    return base64.b64encode(buf.getvalue()).decode()


def apply_theme(opacity=0.30):
    """Background graphic + styling for the full-screen button. Call once, in app.py."""
    st.markdown(f"""
<style>
.stApp {{
    background-image: url("data:image/jpeg;base64,{_bg_uri(opacity)}");
    background-repeat: no-repeat;
    background-position: right top;
    background-size: auto 100vh;
    background-attachment: fixed;
}}
/* full-screen button: right-aligned above each chart */
[class*="st-key-fs_"] {{ display: flex; justify-content: flex-end; }}
[class*="st-key-fs_"] button {{ color: #00549E; font-weight: 600; }}
/* full-screen pop-up: nearly the whole window */
div[data-testid="stDialog"] div[role="dialog"] {{ width: 96vw; max-width: 96vw; }}
</style>
""", unsafe_allow_html=True)


def install_fullscreen():
    """Give every st.plotly_chart a permanent 'Full screen' button and hide the hover toolbar."""
    if getattr(st.plotly_chart, "_kuramo", False):
        return
    original = st.plotly_chart

    def plotly_chart(fig, *args, **kwargs):
        kwargs["config"] = {**kwargs.get("config", {}), "displayModeBar": False}
        key = "fs_" + hashlib.md5(fig.to_json().encode()).hexdigest()[:12]
        _, btn = st.columns([3, 1])
        if btn.button("Full screen", key=key, icon=":material/fullscreen:", type="tertiary"):
            @st.dialog("Full screen view", width="large")
            def _show():
                big = go.Figure(fig)
                big.update_layout(height=720)
                original(big, **kwargs)
            _show()
        original(fig, *args, **kwargs)

    plotly_chart._kuramo = True
    st.plotly_chart = plotly_chart


@st.cache_resource
def _logo():
    img = Image.open("kuramo_logo.jpg").convert("RGB")
    diff = ImageChops.difference(img, Image.new("RGB", img.size, (255, 255, 255)))
    img = img.crop(diff.point(lambda p: 255 if p > 12 else 0).getbbox())   # trim white margins
    arr = np.asarray(img, dtype=float)
    alpha = ((255 - arr.min(axis=2)) * 1.6).clip(0, 255)                    # white -> transparent
    rgba = np.dstack([arr, alpha]).astype("uint8")
    return Image.fromarray(rgba, "RGBA")


def sidebar_logo(width=230):
    """Kuramo logo at the top of the filter panel (SVG if available, else the JPG)."""
    from pathlib import Path
    svg = Path("kuramo_logo.svg")
    if svg.exists():
        st.sidebar.image(svg.read_text(encoding="utf-8"), width=width)
    else:
        st.sidebar.image(_logo(), width=width)