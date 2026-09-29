"""Display the reservoir data and a row-oriented series table."""

from pathlib import Path

import pandas as pd
import streamlit as st


DATA_PATH = Path(__file__).resolve().parent.parent / "reservoirs.csv"
NON_DATA_COLUMNS = {"omrnr", "iso_aar", "iso_uke"}


@st.cache_data
def load_reservoir_data() -> pd.DataFrame:
    """Read the course CSV from the project root."""
    return pd.read_csv(DATA_PATH)


def get_date_column(data: pd.DataFrame) -> str:
    """Find the column containing the observations' dates."""
    for column in data.columns:
        converted_values = pd.to_datetime(data[column], errors="coerce")
        if converted_values.notna().mean() > 0.9:
            return column
    raise ValueError("No date column was detected in reservoirs.csv.")


def get_data_columns(data: pd.DataFrame, date_column: str) -> list[str]:
    """Return numeric reservoir measures, excluding year/week identifiers."""
    numeric_columns = data.select_dtypes(include="number").columns.tolist()
    return [
        column
        for column in numeric_columns
        if column != date_column and column not in NON_DATA_COLUMNS
    ]


def prepare_national_series(data: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    """Prepare the national reservoir series for the compact table."""
    date_column = get_date_column(data)
    data_with_dates = data.copy()
    data_with_dates[date_column] = pd.to_datetime(
        data_with_dates[date_column], errors="coerce"
    )
    data_with_dates = data_with_dates.dropna(subset=[date_column])

    # The CSV contains national, electricity-area, and water-area rows.
    # Use the national aggregate so each measure has one clear time series.
    if {"omrType", "omrnr"}.issubset(data_with_dates.columns):
        national_rows = data_with_dates[
            data_with_dates["omrType"].eq("NO")
            & data_with_dates["omrnr"].eq(0)
        ]
        if not national_rows.empty:
            data_with_dates = national_rows

    data_columns = get_data_columns(data_with_dates, date_column)
    if not data_columns:
        raise ValueError("No numeric reservoir measures were found in reservoirs.csv.")

    prepared_data = (
        data_with_dates[[date_column, *data_columns]]
        .groupby(date_column, as_index=False)
        .mean(numeric_only=True)
        .sort_values(date_column)
        .reset_index(drop=True)
    )
    return prepared_data, date_column


def prepare_series_table(data: pd.DataFrame) -> pd.DataFrame:
    """Transform the column-oriented CSV into one row for every data column.

    The original CSV stores each series in a column. Streamlit's
    ``LineChartColumn`` expects a list of values in one table cell, so each
    numeric column becomes one row and its complete series becomes a list.
    """
    prepared_data, date_column = prepare_national_series(data)
    first_month = prepared_data[date_column].dt.to_period("M").iloc[0]
    first_month_data = prepared_data[
        prepared_data[date_column].dt.to_period("M").eq(first_month)
    ]
    data_columns = [column for column in prepared_data.columns if column != date_column]
    rows = []
    for column in data_columns:
        values = first_month_data[column].dropna().tolist()
        rows.append(
            {
                "Data column": column,
                "First date": first_month_data[date_column].iloc[0].date(),
                "First month": values[0] if values else None,
                "Series": values,
            }
        )
    return pd.DataFrame(rows)


st.title("Reservoir Data")
st.write("The imported data is shown below. The CSV must be in the project root.")

if not DATA_PATH.exists():
    st.error(
        "reservoirs.csv was not found. Add the real course file to the project "
        "root before loading the data."
    )
    st.stop()

try:
    reservoir_data = load_reservoir_data()
except (OSError, pd.errors.ParserError) as error:
    st.error(f"The CSV could not be read: {error}")
    st.stop()

st.subheader("Imported data")
st.dataframe(reservoir_data, use_container_width=True)

try:
    series_table = prepare_series_table(reservoir_data)
except ValueError as error:
    st.error(str(error))
    st.stop()

if series_table.empty:
    st.warning("No reservoir measures were detected in reservoirs.csv.")
else:
    st.subheader("One row per data column")
    st.caption("The Line chart column shows each series during its first calendar month.")
    st.dataframe(
        series_table,
        column_config={
            "Series": st.column_config.LineChartColumn(
                "Series (all dates)"
            )
        },
        hide_index=True,
        use_container_width=True,
    )