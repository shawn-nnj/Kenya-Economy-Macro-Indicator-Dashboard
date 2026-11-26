# Kenya Economy Dashboard

An interactive Streamlit dashboard showing what drives Kenya's GDP growth and how each
sector contributes, built with Python, pandas and Plotly.

**Live app:** https://YOUR-APP-NAME.streamlit.app

## What it shows
- **Growth drivers:** contribution of each sector to real GDP growth, 2017 to 2023
- **Sector analysis:** share of GDP, real growth, contribution and sub-sector breakdown for each sector

## Method
Contribution to growth = change in a sector's real output (constant 2016 prices) divided by the
previous year's GDP, in percentage points. Contributions add up to real GDP growth.

## Data
Kenya National Bureau of Statistics (KNBS), GDP by activity. 2022 and 2023 figures are provisional.

## Run locally
    pip install -r requirements.txt
    python -m streamlit run app.py