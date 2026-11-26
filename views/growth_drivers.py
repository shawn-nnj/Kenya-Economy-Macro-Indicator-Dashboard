import textwrap

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

/* sidebar opener labelled "Menu" */
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
    content: "Menu"; color: white; font-weight: 600; font-size: 0.95rem;
}
</style>
""", unsafe_allow_html=True)

BLUE, GREY, RED = "#1F4E79", "#C9CED6", "#C0392B"
YEARS = list(range(2017, 2024))
CHART_H = 720


# ---------- data ----------
@st.cache_data
def load():
    def get(name):
        return pd.read_csv(f"{name}.csv").set_index("Industry")
    contrib, nom = get("contrib"), get("nom")
    gdp = pd.read_csv("gdp.csv").set_index("Year")["GDP at market prices"]
    for d in (contrib, nom):
        d.columns = [int(c) for c in d.columns]
    nom = nom.loc[nom.index.isin(contrib.index)]
    return contrib, nom, gdp


contrib, nom, gdp = load()


def kpi_name(name, limit=None):
    return display_name(name)                     # full name, never cut


def axis_name(name, width=26):
    return "<br>".join(textwrap.wrap(display_name(name), width))   # wrap long names, don't cut


def growth_of(y):
    return (gdp[y] / gdp[y - 1] - 1) * 100 if (y - 1) in gdp.index else None


# ---------- header + clickable year ----------
st.title(":material/trending_up: Growth Drivers: What Moved Kenya's GDP")
st.caption("Which sectors pushed Kenya's economy forward each year, and which held it back. "
           "Pick a year to update every number and chart below.")

year = st.segmented_control("Year", options=YEARS, default=2023,
                            label_visibility="collapsed")
if year is None:
    year = 2023

st.subheader(f"{year} at a Glance")
st.caption("Headline numbers for the selected year, compared with the year before.")

# ---------- numbers for the selected year ----------
c_year = contrib[year].dropna().sort_values(ascending=False)
g, g_prev = growth_of(year), growth_of(year - 1)
nom_now = nom[year].sum() / 1e6
nom_prev = nom[year - 1].sum() / 1e6 if (year - 1) in nom.columns else None
lead_name, lead_val = c_year.index[0], float(c_year.iloc[0])
worst_name, worst_val = c_year.index[-1], float(c_year.iloc[-1])
top4 = float(c_year.head(4).sum())

# ---------- KPI cards ----------
k1, k2, k3, k4 = st.columns(4)
k1.metric(":material/trending_up: Real GDP Growth", f"{g:.1f}%",
          f"{g - g_prev:+.1f} pp vs {year - 1}" if g_prev is not None else "First year in series",
          delta_color="normal" if g_prev is not None else "off",
          help="Growth in GDP after removing the effect of price changes.")
k2.metric(":material/payments: Nominal GDP", f"KSh {nom_now:.1f} tn",
          f"{(nom_now / nom_prev - 1) * 100:+.1f}% vs {year - 1}" if nom_prev else "First year in series",
          delta_color="normal" if nom_prev else "off",
          help="Size of the economy at current prices, in KSh trillion.")
k3.container(key="kpi_name_a").metric(
    ":material/emoji_events: Leading Contributor", kpi_name(lead_name),
    f"{lead_val:+.2f} pp of growth", delta_color="off",
    help=f"{display_name(lead_name)} added {lead_val:.2f} percentage points to the "
         f"{g:.1f}% real GDP growth in {year}.")
if worst_val < 0:
    k4.container(key="kpi_name_b").metric(
        ":material/trending_down: Largest Detractor", kpi_name(worst_name),
        f"{worst_val:+.2f} pp of growth",
        help=f"{display_name(worst_name)} took {abs(worst_val):.2f} percentage points "
             f"off real GDP growth in {year}.")
else:
    names = ", ".join(display_name(n) for n in c_year.head(4).index)
    share4 = top4 / c_year.sum() * 100 if c_year.sum() else 0
    k4.metric(":material/groups: Top-4 Sectors", f"{share4:.0f}%", "of total growth",
              delta_color="off", help=f"The four largest contributors: {names}.")

st.write("")


# ---------- charts ----------
def drivers_chart(y):
    s = contrib[y].dropna().sort_values()
    total = float(s.sum())
    third = round(float(s.sort_values(ascending=False).iloc[2]), 2)   # 3rd-largest, as displayed
    colors = [RED if v < 0 else (BLUE if round(float(v), 2) >= third and v > 0 else GREY)
              for v in s.values]
    names = [axis_name(n) for n in s.index]
    vals = [float(v) for v in s.values]

    fig = go.Figure(go.Bar(
        x=vals, y=names, orientation="h", marker_color=colors,
        text=[f"{v:+.2f}" if v >= 0 else "" for v in vals],      # positives labelled at bar end
        textposition="outside", cliponaxis=False))
    neg = [(n, v) for n, v in zip(names, vals) if v < 0]
    if neg:                                                       # negatives labelled right of zero
        fig.add_trace(go.Scatter(
            x=[0] * len(neg), y=[n for n, _ in neg], mode="text",
            text=[f"  {v:+.2f}" for _, v in neg], textposition="middle right",
            textfont=dict(color=RED, size=12), showlegend=False, hoverinfo="skip"))

    span = max(vals) - min(0, min(vals))
    fig.update_layout(
        font=dict(color="#222"), paper_bgcolor="white", plot_bgcolor="white",
        height=CHART_H, margin=dict(l=220, r=30, t=30, b=60), showlegend=False,
        xaxis=dict(title="Contribution (percentage points)",
                   showgrid=True, gridcolor="#EEF1F5", zeroline=True,
                   zerolinecolor="#999", color="#222",
                   range=[min(0, min(vals)) - 0.06 * span, max(vals) + 0.16 * span]),
        yaxis=dict(color="#222", automargin=True, tickfont=dict(size=12)))
    if total > 0:
        t4 = s.sort_values(ascending=False).head(4).sum() / total * 100
        finding = (f"{display_name(s.index[-1])} added {s.iloc[-1]:.2f} pp of the "
                   f"{total:.1f}% growth in {y}; the top four sectors drove {t4:.0f}% of it.")
    else:
        finding = f"Sector contributions netted to {total:.1f}% in {y}."
    return fig, finding


def trend_chart(selected):
    vals = [growth_of(y) for y in YEARS]
    colors = [RED if y == 2020 else BLUE if y == 2021 else GREY for y in YEARS]
    outline = ["#111111" if y == selected else "rgba(0,0,0,0)" for y in YEARS]
    fig = go.Figure(go.Bar(
        x=[str(y) for y in YEARS], y=[float(v) for v in vals], marker_color=colors,
        marker_line_color=outline, marker_line_width=2.5,
        text=[f"{v:.1f}%" for v in vals], textposition="outside", cliponaxis=False))
    i20, i21 = YEARS.index(2020), YEARS.index(2021)
    fig.add_annotation(x=i20, y=vals[i20], text="COVID-19", showarrow=False,
                       yshift=-28, font=dict(size=11, color=RED))
    fig.add_annotation(x=i21, y=vals[i21], text="Rebound", showarrow=False,
                       yshift=34, font=dict(size=11, color=BLUE))
    fig.update_layout(
        font=dict(color="#222"), paper_bgcolor="white", plot_bgcolor="white",
        height=CHART_H, margin=dict(l=70, r=20, t=30, b=60), showlegend=False,
        xaxis=dict(type="category", color="#222"),
        yaxis=dict(title="Real GDP growth (%)", showgrid=True, gridcolor="#EEF1F5",
                   zeroline=True, zerolinecolor="#999", color="#222",
                   range=[-2, max(float(v) for v in vals) + 2.5], automargin=True))
    v20, v21 = vals[i20], vals[i21]
    word = "shrank" if v20 < 0 else "grew only"
    finding = (f"The economy {word} {abs(v20):.1f}% in 2020 because of COVID-19, "
               f"then rebounded {v21:.1f}% in 2021.")
    return fig, finding


fig_d, find_d = drivers_chart(year)
fig_t, find_t = trend_chart(year)
left, right = st.columns(2)

with left.container(key="card_drivers"):
    section(":material/leaderboard: Contribution by Sector",
            f"How many percentage points each sector added to, or took from, real GDP growth "
            f"in {year}. Blue marks the largest contributors and red any drag.",
            find_d, min_h=150)
    st.plotly_chart(fig_d, theme=None)

with right.container(key="card_trend"):
    section(":material/show_chart: Real GDP Growth Over Time",
            f"Annual real GDP growth, 2017 to 2023. The selected year ({year}) has a dark "
            f"outline; COVID-19 is shown in red and the rebound in blue.",
            find_t, min_h=150)
    st.plotly_chart(fig_t, theme=None)

st.caption("Contribution to growth = change in a sector's real output divided by the "
           "previous year's GDP, in percentage points; contributions add up to real GDP growth. "
           "Nominal GDP is the sum of sector value added at current prices.")
st.caption("Source: Kenya National Bureau of Statistics (KNBS), GDP by activity; "
           "author's calculations. 2022 and 2023 figures are provisional and may be revised.")