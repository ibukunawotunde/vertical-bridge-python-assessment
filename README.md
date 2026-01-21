This repository contains my take-home submission for the Data Science Analyst role at Vertical Bridge. The project demonstrates a clean, reproducible workflow for analyzing a site list export (Excel/CSV) using Python.

Key deliverables implemented:

- Load the dataset into a DataFrame named vertical_bridge
- Feature engineering: extract state from Site No and place it directly beside Site No
- Data filtering: remove records without Date Start and exclude TWR-IP variants
- Reporting: summary table of site counts by Site Type
- Visualization: interactive Plotly multi-line chart of average Overall Structure Height (AGL) by Year Built, segmented by Site Type

The code is organized following standard project structure (src/, requirements.txt, .gitignore, README.md) and can be run locally in a virtual environment. Outputs are exported to outputs/ including CSV summaries and an interactive HTML chart for easy review.
