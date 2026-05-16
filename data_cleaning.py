"""
Cricket Analytics - Complete Data Cleaning Script
Handles spaces, missing values, and type conversions for all CSV files

Author: Cricket Analytics Team
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Any

import numpy as np
import pandas as pd


# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------

CSV_FILES: Dict[str, str] = {
    "odi_batting": "odi_batting.csv",
    "odi_bowling": "odi_bowling.csv",
    "odi_fielding": "odi_fielding.csv",
    "t20_batting": "t20_batting.csv",
    "t20_bowling": "t20_bowling.csv",
    "t20_fielding": "t20_fielding.csv",
    "test_batting": "test_batting.csv",
    "test_bowling": "test_bowling.csv",
    "test_fielding": "test_fielding.csv",
}

NUMERIC_MAPPINGS = {
    "batting": ["Mat", "Inns", "NO", "Runs", "HS", "Ave", "BF", "SR", "100", "50", "0"],
    "bowling": ["Mat", "Inns", "Balls", "Runs", "Wkts", "Ave", "Econ", "SR", "4", "5", "10"],
    "fielding": ["Mat", "Inns", "Ct", "St", "Dis"],
}

# For generic conversions (quick_clean, streamlit)
GENERIC_NUMERIC_COLS = [
    "Mat",
    "Inns",
    "NO",
    "Runs",
    "HS",
    "Ave",
    "BF",
    "SR",
    "100",
    "50",
    "0",
    "Balls",
    "Wkts",
    "Econ",
    "4",
    "5",
    "10",
    "Overs",
    "Ct",
    "St",
    "Dis",
]


# -------------------------------------------------------------------
# Core cleaning helpers
# -------------------------------------------------------------------

def _strip_columns_and_strings(df: pd.DataFrame) -> pd.DataFrame:
    """Strip spaces from column names and string values."""
    df = df.copy()
    df.columns = df.columns.str.strip()

    object_cols = df.select_dtypes(include=["object"]).columns
    for col in object_cols:
        df[col] = df[col].astype(str).str.strip()

    return df


def _convert_numeric_columns(
    df: pd.DataFrame, numeric_cols: list[str], extra_numeric: list[str] | None = None
) -> pd.DataFrame:
    """Convert specified columns to numeric, coercing errors to NaN."""
    df = df.copy()
    cols_to_convert = set(numeric_cols)
    if extra_numeric:
        cols_to_convert.update(extra_numeric)

    for col in cols_to_convert:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def _fill_missing(df: pd.DataFrame) -> pd.DataFrame:
    """Fill NaN in numeric with 0, others with 'Unknown'."""
    df = df.copy()
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(0)
        else:
            df[col] = df[col].fillna("Unknown")
    return df


def _remove_duplicates_and_sort(df: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicates by Player+Span (if available) and sort by Player."""
    df = df.copy()

    if {"Player", "Span"}.issubset(df.columns):
        df = df.drop_duplicates(subset=["Player", "Span"], keep="first")

    if "Player" in df.columns:
        df = df.sort_values("Player").reset_index(drop=True)

    return df


def _get_file_type(filename: str) -> str:
    """Infer file type from filename."""
    filename = filename.lower()
    if "batting" in filename:
        return "batting"
    if "bowling" in filename:
        return "bowling"
    return "fielding"


# -------------------------------------------------------------------
# Public cleaning functions
# -------------------------------------------------------------------

def clean_single_dataframe(df: pd.DataFrame, filename: str | None = None) -> pd.DataFrame:
    """
    Clean a single cricket stats dataframe:
    - strip spaces
    - convert numeric columns
    - fill missing values
    - remove duplicates and sort
    """
    df = _strip_columns_and_strings(df)

    if "Player" in df.columns:
        df["Player"] = df["Player"].astype(str).str.strip()

    file_type = _get_file_type(filename or "")

    numeric_cols = NUMERIC_MAPPINGS.get(file_type, [])
    extra_numeric = []

    # Special case for T20 bowling (Overs instead of Balls)
    if filename and "t20_bowling" in filename.lower() and "Overs" in df.columns:
        extra_numeric.append("Overs")

    df = _convert_numeric_columns(df, numeric_cols, extra_numeric=extra_numeric)
    df = _fill_missing(df)
    df = _remove_duplicates_and_sort(df)

    return df


def clean_csv_files(
    csv_directory: str | os.PathLike = ".", output_directory: str | os.PathLike = "cleaned_data"
) -> Dict[str, pd.DataFrame]:
    """
    Clean all cricket CSV files in a directory and save them.

    Returns:
        Dictionary {name: cleaned_dataframe}
    """
    csv_dir = Path(csv_directory)
    out_dir = Path(output_directory)
    out_dir.mkdir(parents=True, exist_ok=True)

    cleaned_data: Dict[str, pd.DataFrame] = {}

    for name, filename in CSV_FILES.items():
        filepath = csv_dir / filename

        if not filepath.exists():
            print(f"❌ File not found: {filename}")
            continue

        try:
            print(f"\n🔄 Processing: {filename}")
            print("-" * 50)

            df = pd.read_csv(filepath)
            print(f"✓ Loaded: {df.shape[0]} rows, {df.shape[1]} columns")

            df_clean = clean_single_dataframe(df, filename=filename)

            print(f"\n✅ Cleaning completed!")
            print(f"   Final rows: {df_clean.shape[0]}")
            print(f"   Columns: {list(df_clean.columns)}")

            print("\n   Sample data:")
            print(df_clean.head(2).to_string())
            print()

            output_path = out_dir / filename
            df_clean.to_csv(output_path, index=False)
            print(f"   📁 Saved to: {output_path}")

            cleaned_data[name] = df_clean

        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")
            continue

    return cleaned_data


def validate_and_report(cleaned_data: Dict[str, pd.DataFrame]) -> None:
    """
    Validate cleaned data and generate a console report.

    Args:
        cleaned_data: Dictionary of cleaned dataframes
    """
    print("\n" + "=" * 70)
    print("📊 VALIDATION REPORT")
    print("=" * 70)

    for name, df in cleaned_data.items():
        print(f"\n📄 {name.upper()}")
        print("-" * 70)

        # Missing values
        missing = df.isnull().sum()
        if (missing > 0).any():
            print("⚠️  Missing values detected:")
            print(missing[missing > 0].to_string())
        else:
            print("✅ No missing values")

        # Data types
        print("📝 Data types:")
        for col, dtype in df.dtypes.items():
            print(f"   {col}: {dtype}")

        # Numeric summary
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            print("\n🔢 Numeric columns summary:")
            print(df[numeric_cols].describe().to_string())

        # Leading/trailing spaces check
        string_cols = df.select_dtypes(include=["object"]).columns
        spaces_found = False
        for col in string_cols:
            if df[col].str.contains(r"^ | $", regex=True, na=False).any():
                print(f"⚠️  Leading/trailing spaces found in {col}")
                spaces_found = True

        if not spaces_found and len(string_cols) > 0:
            print("✅ No leading/trailing spaces in string columns")

        print()


def quick_clean(filename: str) -> pd.DataFrame:
    """
    Quick clean a single CSV file and return the cleaned dataframe.
    """
    print(f"🔄 Quick cleaning: {filename}")

    df = pd.read_csv(filename)
    df = _strip_columns_and_strings(df)
    df = _convert_numeric_columns(df, GENERIC_NUMERIC_COLS)
    df = _fill_missing(df)

    if "Player" in df.columns:
        df = df.sort_values("Player").reset_index(drop=True)

    print(f"✅ Cleaned: {df.shape[0]} rows, {df.shape[1]} columns")
    return df


def apply_cleaning_to_streamlit(data_dict: Dict[str, Dict[str, pd.DataFrame]]) -> Dict[str, Dict[str, pd.DataFrame]]:
    """
    Apply cleaning (light) to data dictionary used in Streamlit app.

    Args:
        data_dict: {format: {type: dataframe}}

    Returns:
        Cleaned data_dict (in-place modified but also returned for convenience)
    """
    for format_key, type_dict in data_dict.items():
        for type_key, df in type_dict.items():
            df = df.copy()
            df = _strip_columns_and_strings(df)
            df = _convert_numeric_columns(df, GENERIC_NUMERIC_COLS)

            # Only fill NaN for numeric to preserve category labels if needed
            for col in df.columns:
                if pd.api.types.is_numeric_dtype(df[col]):
                    df[col] = df[col].fillna(0)

            data_dict[format_key][type_key] = df

    return data_dict


# -------------------------------------------------------------------
# Script entry point
# -------------------------------------------------------------------

if __name__ == "__main__":
    print("🏏 CRICKET ANALYTICS - DATA CLEANING TOOL\n")

    # Method 1: Clean all files in current directory
    print("=" * 70)
    print("METHOD 1: Clean all CSV files in current directory")
    print("=" * 70)

    cleaned_data = clean_csv_files(csv_directory=".", output_directory="cleaned_data")

    # Method 2: Validate cleaned data
    print("\n" + "=" * 70)
    print("METHOD 2: Validate cleaned data")
    print("=" * 70)

    if cleaned_data:
        validate_and_report(cleaned_data)

    # Method 3: Quick clean single file (uncomment to use)
    print("\n" + "=" * 70)
    print("METHOD 3: Quick clean single file (example)")
    print("=" * 70)
    # example: quick_clean("odi_batting.csv")

    print("\n✅ Data cleaning complete!")
    print("\n📍 Cleaned files saved in: 'cleaned_data' folder")
    print("📍 Use cleaned files in your Streamlit app")

    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    print(f"Total files cleaned: {len(cleaned_data)}")
    for name in cleaned_data:
        print(f"  ✓ {name}")
