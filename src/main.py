"""
Vertical Bridge — Python Assessment (main script)

Tasks:
1) Create a dataframe from the Excel/CSV file
2) Extract state from Site No into a new column: state
3) Create summary table: number of sites per Site Type
   - filter out rows without Date Start
   - filter out TWR-IP variants (TWR-IP, TWR IP, TWR - IP, etc.)
4) Multi-line chart: Year Built (x) vs avg Overall Structure Height (AGL) (y), one line per Site Type

Outputs saved to ./outputs:
- site_type_summary_filtered.csv
- filtered_sites_with_state.csv
- avg_height_by_year_site_type.csv
- avg_height_by_year_site_type.png
"""

from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


REQUIRED_COLS = [
    "Site No",
    "Date Start",
    "Site Type",
    "Overall Structure Height (AGL)",
    "Year Built",
]


def load_data(input_path: Path, sheet: str | None = None) -> pd.DataFrame:
    """Load Excel/CSV into a DataFrame."""
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    suffix = input_path.suffix.lower()

    if suffix == ".csv":
        df = pd.read_csv(input_path)
        df.columns = [str(c).strip() for c in df.columns]
        return df

    if suffix in {".xlsx", ".xls"}:
        xls = pd.ExcelFile(input_path)

        # If sheet not provided, pick the non-empty sheet with the most rows.
        if sheet is None:
            best_sheet = None
            best_rows = -1
            for s in xls.sheet_names:
                tmp = xls.parse(s)
                if tmp is None or tmp.shape[1] == 0:
                    continue
                if len(tmp) > best_rows:
                    best_rows = len(tmp)
                    best_sheet = s
            sheet = best_sheet or xls.sheet_names[0]

        df = xls.parse(sheet)
        df.columns = [str(c).strip() for c in df.columns]
        return df

    raise ValueError(f"Unsupported file type: {suffix}. Use .xlsx/.xls/.csv")


def add_state_column(df: pd.DataFrame) -> pd.DataFrame:
    """Extract 2-letter state from Site No formatted like 'US-AK-0001' -> 'AK'."""
    out = df.copy()
    out["state"] = out["Site No"].astype(str).str.extract(r"^US-([A-Z]{2})-")
    return out


def filter_sites(df: pd.DataFrame, require_start_date: bool = True, exclude_twr_ip: bool = True) -> pd.DataFrame:
    """
    Filter rows:
    - keep only those with Date Start (if require_start_date=True)
    - exclude TWR-IP variants (if exclude_twr_ip=True)
    """
    out = df.copy()

    # Robust datetime parsing (invalids -> NaT)
    if "Date Start" in out.columns:
        out["Date Start"] = pd.to_datetime(out["Date Start"], errors="coerce")

    # Normalize Site Type to detect TWR-IP variants reliably
    if "Site Type" in out.columns:
        site_type_norm = (
            out["Site Type"]
            .astype(str)
            .str.upper()
            .str.replace(r"[\s\-]", "", regex=True)  # remove spaces/hyphens
        )
    else:
        site_type_norm = pd.Series([""], index=out.index)

    if require_start_date and "Date Start" in out.columns:
        out = out[out["Date Start"].notna()]

    if exclude_twr_ip and "Site Type" in out.columns:
        out = out[site_type_norm != "TWRIP"]

    return out.copy()


def build_site_type_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Count sites per Site Type."""
    if "Site Type" not in df.columns:
        return pd.DataFrame(columns=["Site Type", "Number of Sites"])

    return (
        df.groupby("Site Type")
        .size()
        .reset_index(name="Number of Sites")
        .sort_values("Number of Sites", ascending=False)
        .reset_index(drop=True)
    )


def build_avg_height_by_year_and_type(df: pd.DataFrame) -> pd.DataFrame:
    """Average Overall Structure Height (AGL) by Year Built and Site Type."""
    needed = {"Year Built", "Site Type", "Overall Structure Height (AGL)"}
    if not needed.issubset(df.columns):
        return pd.DataFrame(columns=["Year Built", "Site Type", "Avg Height (AGL)"])

    out = df.copy()
    out["Year Built"] = pd.to_numeric(out["Year Built"], errors="coerce").astype("Int64")

    out = out[
        out["Year Built"].notna() &
        out["Overall Structure Height (AGL)"].notna()
    ].copy()

    return (
        out.groupby(["Year Built", "Site Type"])["Overall Structure Height (AGL)"]
        .mean()
        .reset_index()
        .rename(columns={"Overall Structure Height (AGL)": "Avg Height (AGL)"})
        .sort_values(["Site Type", "Year Built"])
    )


def plot_multiline(avg_df: pd.DataFrame, out_png: Path) -> None:
    """Create and save multi-line plot."""
    if avg_df.empty:
        print("No data available to plot (avg_df is empty).")
        return

    pivot = avg_df.pivot(index="Year Built", columns="Site Type", values="Avg Height (AGL)").sort_index()

    plt.figure(figsize=(12, 6))
    for col in pivot.columns:
        plt.plot(pivot.index, pivot[col], marker="o", label=col)

    plt.title("Average Overall Structure Height (AGL) by Year Built and Site Type")
    plt.xlabel("Year Built")
    plt.ylabel("Average Overall Structure Height (AGL)")
    plt.grid(True)
    plt.legend(title="Site Type", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig(out_png, dpi=200)
    plt.close()


def validate_columns(df: pd.DataFrame) -> None:
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        print(f"WARNING: Missing expected columns: {missing}")
        print("The script will run, but outputs may be incomplete.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Vertical Bridge Python Assessment Solution")
    parser.add_argument(
        "--input",
        type=str,
        default="Python Exercise Data.xlsx",
        help="Path to input Excel/CSV file (default: Python Exercise Data.xlsx)",
    )
    parser.add_argument(
        "--sheet",
        type=str,
        default=None,
        help="Excel sheet name (optional). If omitted, the script picks the best sheet.",
    )
    parser.add_argument(
        "--outputs",
        type=str,
        default="outputs",
        help="Output folder (default: outputs)",
    )
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    out_dir = Path(args.outputs).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1) Load
    df = load_data(input_path, sheet=args.sheet)
    validate_columns(df)

    # 2) State extraction
    df = add_state_column(df)

    # 3) Filter + summary
    filtered = filter_sites(df, require_start_date=True, exclude_twr_ip=True)
    summary = build_site_type_summary(filtered)

    # 4) Avg heights + plot
    avg_df = build_avg_height_by_year_and_type(filtered)
    chart_path = out_dir / "avg_height_by_year_site_type.png"
    plot_multiline(avg_df, chart_path)

    # Save outputs
    summary.to_csv(out_dir / "site_type_summary_filtered.csv", index=False)
    filtered.to_csv(out_dir / "filtered_sites_with_state.csv", index=False)
    avg_df.to_csv(out_dir / "avg_height_by_year_site_type.csv", index=False)

    # Print a clean console summary
    print("\n=== Loaded Data ===")
    print(f"File: {input_path.name}")
    print(f"Rows x Cols: {df.shape[0]:,} x {df.shape[1]:,}")

    print("\n=== Filtered Data (Date Start present, TWR-IP removed) ===")
    print(f"Rows: {len(filtered):,}")

    print("\n=== Site Type Summary (Top 20) ===")
    print(summary.head(20).to_string(index=False))

    print("\n=== Outputs written ===")
    print(f"- {out_dir / 'site_type_summary_filtered.csv'}")
    print(f"- {out_dir / 'filtered_sites_with_state.csv'}")
    print(f"- {out_dir / 'avg_height_by_year_site_type.csv'}")
    print(f"- {chart_path}")


if __name__ == "__main__":
    main()
