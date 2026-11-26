import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from shared import section, display_name

st.markdown("""
<style>
.stApp {background-color: #F3F5F8;}
h1, h2, h3, h5 {color: #1F4E79 !important;}

[data-testid="stMetric"] {
    background: white; border: 1px solid #E1E6EC; border-top: 3px solid #2E86C1;
    border-radius: 10px; padding: 14px 18px;
    box-shadow: 0 1px 3px rgba(16,24,40,0.08);
    box-sizing: border-box; overflow: hidden;
}
[data-testid="stMetricLabel"] {color: #5B6573;}
[data-testid="stMetricValue"], [data-testid="stMetricValue"] * {
    font-size: 1.65rem; font-weight: 700; color: #1F4E79;
    white-space: nowrap; line-height: 1.25;
}
[class*="st-key-card"] {
    background: white; border: 1px solid #E1E6EC; border-top: 3px solid #2E86C1;
    border-radius: 10px; padding: 14px 18px;
    box-shadow: 0 1px 3px rgba(16,24,40,0.08);
}

/* sidebar opener labelled "Filters" */
[data-testid="stExpandSidebarButton"], [data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"], [data-testid*="xpandSidebar"] {
    background: #1F4E79 !important; border-radius: 8px; padding: 4px 12px;
    display: flex !important; align-items: center; gap: 6px; width: auto !important;
}
[data-testid="stExpandSidebarButton"] *, [data-testid="stSidebarCollapsedControl"] *,
[data-testid="collapsedControl"] *, [data-testid*="xpandSidebar"] * {
    color: white !important; fill: white !important;
}
[data-testid="stExpandSidebarButton"]::after, [data-testid="stSidebarCollapsedControl"]::after,
[data-testid="collapsedControl"]::after, [data-testid*="xpandSidebar"]::after {
    content: "Filters"; color: white; font-weight: 600; font-size: 0.95rem;
}
</style>
""", unsafe_allow_html=True)

BLUE, GREY, RED = "#1F4E79", "#C9CED6", "#C0392B"
GDP = "GDP at market prices"

PARENTS = {
 "Agriculture, forestry and fishing": ["Growing of crops", "Animal production",
     "Support activities to agriculture", "Forestry & logging", "Fishing & aquaculture"],
 "Manufacturing": ["Manufacture of food, beverages and tobacco",
     "Other manufacturing and repair and installation"],
 "Transportation and storage": ["Land transport",
     "Air transport including support services",
     "All other transport including postal and courier activities"],
 "Information and communication": ["Telecommunications",
     "Publishing, broadcasting, other IT and information activities"],
 "Financial and insurance activities": ["Financial activities", "Insurance activities"],
 "Education": ["Pre-primary and Primary education",
     "General secondary education", "Higher and other education"],
}

SECTORS = ["Agriculture, forestry and fishing", "Mining and quarrying",
    "Manufacturing", "Electricity supply", "Water supply; sewerage, waste management",
    "Construction", "Wholesale and retail trade; repairs", "Transportation and storage",
    "Accommodation and food service activities", "Information and communication",
    "Financial and insurance activities", "Real estate",
    "Professional, scientific and technical activities",
    "Administrative and support service activities",
    "Public administration and defence", "Education",
    "Human health and social work activities",
    "Arts, entertainment and recreation", "Other service activities",
    "Activities of households as employers;"]


def short(n):
    return display_name(n)


@st.cache_data
def load():
    df = pd.read_csv("gdp_all.csv")
    real = df[df["Prices"] == "Constant"].pivot(
        index="Industry", columns="Year", values="Ksh Million")
    nom = df[df["Prices"] == "Current"].pivot(
        index="Industry", columns="Year", values="Ksh Million")
    return real, nom


real, nom = load()
gdp_r = real.loc[GDP]

# sectors ranked by share of GDP in the latest year (largest first)
LATEST = int(nom.columns.max())
by_size = (nom.loc[SECTORS, LATEST] / nom.loc[GDP, LATEST] * 100).sort_values(ascending=False)
RANKED_SECTORS = list(by_size.index)
SIZE_RANK = {s: i + 1 for i, s in enumerate(RANKED_SECTORS)}

# ---------- filters ----------
st.sidebar.header("Filters")
st.sidebar.markdown("**Sector**")
st.sidebar.caption(f"Ranked by share of GDP in {LATEST}, largest first.")
sector = st.sidebar.selectbox("Sector", RANKED_SECTORS, label_visibility="collapsed",
                              format_func=lambda s: f"{SIZE_RANK[s]}. {short(s)}")
basis = st.sidebar.radio("Prices for the output chart",
                         ["Real (constant 2016)", "Nominal (current)"])
y0, y1 = st.sidebar.select_slider("Period", options=list(range(2016, 2024)),
                                  value=(2016, 2023))
if y0 >= y1:
    st.warning("Choose a period of at least two years.")
    st.stop()
n = y1 - y0
real_basis = basis.startswith("Real")

# ---------- calculations ----------
cagr = ((real.loc[sector, y1] / real.loc[sector, y0]) ** (1 / n) - 1) * 100
gdp_cagr = ((gdp_r[y1] / gdp_r[y0]) ** (1 / n) - 1) * 100
share1 = nom.loc[sector, y1] / nom.loc[GDP, y1] * 100
share0 = nom.loc[sector, y0] / nom.loc[GDP, y0] * 100
cum = (real[y1] - real[y0]) / gdp_r[y0] * 100      # contribution in pp, all rows
contrib_pp, total_pp = cum[sector], cum[GDP]
ranked = cum[SECTORS].sort_values(ascending=False)
rank = list(ranked.index).index(sector) + 1

# ---------- header and KPI cards ----------
st.title(f":material/pie_chart: Sector Analysis: {short(sector)}")
st.caption(f"How big the sector is, how fast it is growing and how much of the economy's "
           f"growth it delivered, {y0} to {y1}. Use the filters on the left to change "
           f"sector, prices or period.")

st.subheader("Key Performance Indicators")
st.caption("Growth figures use real GDP at constant 2016 prices; share of GDP uses "
           "current prices.")

c1, c2, c3, c4 = st.columns(4)
c1.metric(":material/donut_large: Share of GDP", f"{share1:.1f}%",
          f"{share1 - share0:+.1f} pp vs {y0}",
          help=f"{short(sector)} as a share of GDP at current prices in {y1}.")
c2.metric(":material/speed: Real Growth per Year", f"{cagr:.1f}%",
          f"{cagr - gdp_cagr:+.1f} pp vs economy ({gdp_cagr:.1f}%)",
          help="Compound annual growth rate of real output over the selected period.")
c3.metric(":material/add_chart: Contribution to Growth", f"{contrib_pp:.1f} pp",
          f"{contrib_pp / total_pp * 100:.0f}% of {total_pp:.0f}% total", delta_color="off",
          help="Percentage points of total real GDP growth that came from this sector.")
c4.metric(":material/leaderboard: Rank by Contribution", f"#{rank} of {len(SECTORS)}",
          f"Top: {short(ranked.index[0])}", delta_color="off",
          help=f"Ranked by contribution to real GDP growth, {y0} to {y1}. "
               f"The top contributor is {short(ranked.index[0])}.")

st.write("")

# ---------- chart 1: output over time ----------
tbl = real if real_basis else nom
yrs = list(range(y0, y1 + 1))
vals = [float(tbl.loc[sector, y] / 1000) for y in yrs]          # KSh billion
c_basis = ((vals[-1] / vals[0]) ** (1 / n) - 1) * 100
find1 = (f"{short(sector)} output rose from KSh {vals[0]:,.0f} bn to KSh {vals[-1]:,.0f} bn "
         f"({'real' if real_basis else 'nominal'}), {c_basis:.1f}% a year.")
fig1 = go.Figure(go.Bar(x=[str(y) for y in yrs], y=vals, marker_color=BLUE,
                        text=[f"{v:,.0f}" for v in vals], textposition="outside",
                        cliponaxis=False))
fig1.update_layout(font=dict(color="#222"), paper_bgcolor="white", plot_bgcolor="white",
                   height=380, showlegend=False, margin=dict(l=10, r=10, t=30, b=40),
                   xaxis=dict(type="category", showgrid=False, color="#222"),
                   yaxis=dict(visible=False, range=[0, max(vals) * 1.15]))

# ---------- chart 2: growth vs the economy ----------
gy = list(range(y0 + 1, y1 + 1))
sg = [float((real.loc[sector, y] / real.loc[sector, y - 1] - 1) * 100) for y in gy]
eg = [float((gdp_r[y] / gdp_r[y - 1] - 1) * 100) for y in gy]
ahead = sum(a > b for a, b in zip(sg, eg))
find2 = f"{short(sector)} grew faster than the economy in {ahead} of {len(gy)} years."
cats = [str(y) for y in gy]
fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=cats, y=eg, name="Economy (GDP)",
                          mode="lines+markers", line=dict(color="#9AA3AF", dash="dash")))
fig2.add_trace(go.Scatter(x=cats, y=sg, name=short(sector),
                          mode="lines+markers", line=dict(color=BLUE, width=3)))
# labels in white boxes: above the point when the sector is above the economy, below otherwise
for i, (s_, e_) in enumerate(zip(sg, eg)):
    fig2.add_annotation(x=i, y=s_, text=f"{s_:.1f}%", showarrow=False,
                        yshift=20 if s_ >= e_ else -20,
                        bgcolor="rgba(255,255,255,0.92)", borderpad=2,
                        font=dict(size=12, color=BLUE))
lo, hi = min(min(sg), min(eg)), max(max(sg), max(eg))
fig2.update_layout(font=dict(color="#222"), paper_bgcolor="white", plot_bgcolor="white",
                   height=380, margin=dict(l=80, r=20, t=30, b=40),
                   legend=dict(orientation="h", y=1.12, x=0),
                   xaxis=dict(type="category", showgrid=False, color="#222"),
                   yaxis=dict(showgrid=True, gridcolor="#EEF1F5", zeroline=True,
                              zerolinecolor="#999", color="#222", ticksuffix="%",
                              automargin=True, title_standoff=14,
                              range=[lo - 3, hi + 3]))
fig2.update_yaxes(title_text="Real growth, % per year")

left, right = st.columns(2)
with left.container(key="card_size"):
    section(":material/bar_chart: Sector Output Over Time",
            f"Value of everything the sector produced each year, in KSh billion "
            f"({'constant 2016 prices' if real_basis else 'current prices'}).",
            find1, min_h=110)
    st.plotly_chart(fig1, theme=None)
with right.container(key="card_growth"):
    section(":material/show_chart: Growth Against the Economy",
            "Annual real growth of the sector (blue) compared with the whole economy "
            "(grey dashed).",
            find2, min_h=110)
    st.plotly_chart(fig2, theme=None)

# ---------- chart 3: what is inside the sector ----------
kids = PARENTS.get(sector, [])
with st.container(key="card_sub"):
    if not kids:
        section(":material/account_tree: Inside the Sector",
                "Which parts of the sector drove its growth.",
                f"{short(sector)} is reported as a single line, so there is no breakdown.")
        st.info("This sector is reported as a single line, so there is nothing to drill into.")
    else:
        d = pd.Series({k: real.loc[k, y1] - real.loc[k, y0] for k in kids})
        sec_delta = real.loc[sector, y1] - real.loc[sector, y0]
        pp = (d / real.loc[sector, y0] * 100).sort_values()
        top = pp.idxmax()
        if sec_delta > 0:
            find3 = (f"{top} supplied {d[top] / sec_delta * 100:.0f}% of "
                     f"{short(sector)} growth since {y0}.")
        else:
            find3 = f"{short(sector)} output fell between {y0} and {y1}; {top} fared best."
        colors = [RED if v < 0 else (BLUE if k == top else GREY) for k, v in pp.items()]
        fig3 = go.Figure(go.Bar(x=[float(v) for v in pp.values], y=list(pp.index),
                                orientation="h", marker_color=colors,
                                text=[f"{v:+.1f}" for v in pp.values],
                                textposition="outside", cliponaxis=False))
        fig3.update_layout(font=dict(color="#222"), paper_bgcolor="white",
                           plot_bgcolor="white", height=120 + 60 * len(kids),
                           showlegend=False, margin=dict(l=300, r=60, t=20, b=50),
                           xaxis=dict(title=f"Contribution to {short(sector)} growth, "
                                            f"{y0} to {y1} (percentage points)",
                                      showgrid=False, color="#222",
                                      range=[min(0, pp.min()) - 2, pp.max() * 1.2 + 2]),
                           yaxis=dict(showgrid=False, color="#222", automargin=True))
        section(":material/account_tree: Inside the Sector",
                f"Which parts of {short(sector)} drove its growth between {y0} and {y1}. "
                f"Blue marks the biggest contributor and red any drag.",
                find3)
        st.plotly_chart(fig3, theme=None)

st.caption("Contribution to growth = change in real output ÷ starting-year output, "
           "in percentage points (pp). Sub-sector bars sum to the sector's total growth.")
st.caption("Source: Kenya National Bureau of Statistics (KNBS), GDP by activity; "
           "author's calculations. 2022 and 2023 figures are provisional and may be revised.")