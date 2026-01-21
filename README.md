# Vertical Bridge — Python Assessment

## What this does
1. Loads the site list into a DataFrame named `vertical_bridge`
2. Extracts `state` from `Site No` and inserts `state` directly after `Site No`
3. Filters out rows with missing `Date Start` and excludes `TWR-IP` variants, then summarizes counts by `Site Type`
4. Builds an interactive Plotly multi-line chart:
   - X: Year Built
   - Y: Avg Overall Structure Height (AGL)
   - One line per Site Type

## Run locally
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt


