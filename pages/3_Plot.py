"""Plot selected reservoir series from the course CSV."""

from pathlib import Path

import matplotlib.pyplot as plt
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
    """Prepare the national reservoir series with dates as the x-axis."""
    date_column = get_date_column(data)
    data_with_dates = data.copy()
    data_with_dates[date_column] = pd.to_datetime(
        data_with_dates[date_column], errors="coerce"
    )
    data_with_dates = data_with_dates.dropna(subset=[date_column])

    # The CSV contains national, electricity-area, and water-area rows.
    # Use the national aggregate when those identifiers are available.
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


def scale_to_first_date(data: pd.DataFrame) -> pd.DataFrame:
    """Scale each series to 100 at its first displayed date when possible."""
    first_values = data.iloc[0].replace(0, pd.NA)
    scaled_data = data.divide(first_values).multiply(100)
    return scaled_data.fillna(data)


st.title("Reservoir Plot")

if not DATA_PATH.exists():
    st.error(
        "reservoirs.csv was not found. Add the real course file to the project "
        "root before plotting the data."
    )
    st.stop()

try:
    reservoir_data = load_reservoir_data()
except (OSError, pd.errors.ParserError) as error:
    st.error(f"The CSV could not be read: {error}")
    st.stop()

try:
    plot_source, date_column = prepare_national_series(reservoir_data)
except ValueError as error:
    st.error(str(error))
    st.stop()

data_columns = [column for column in plot_source.columns if column != date_column]

selected_column = st.selectbox(
    "Data series",
    options=["All columns", *data_columns],
)

month_options = (
    plot_source[date_column]
    .dt.to_period("M")
    .astype(str)
    .drop_duplicates()
    .tolist()
)
selected_month = st.select_slider(
    "Show data through month",
    options=month_options,
    value=month_options[0],
)

selected_data = plot_source.loc[
    plot_source[date_column].dt.to_period("M").astype(str).le(selected_month),
    [date_column, *data_columns],
]
if selected_column == "All columns":
    plot_data = scale_to_first_date(selected_data[data_columns])
    y_axis_label = "Relative value (first displayed month = 100)"
else:
    plot_data = selected_data[[selected_column]]
    y_axis_label = selected_column

figure, axis = plt.subplots(figsize=(10, 5))
for column in plot_data.columns:
    axis.plot(selected_data[date_column], plot_data[column], label=column)

axis.set_title("National reservoir data over time")
axis.set_xlabel("Date")
axis.set_ylabel(y_axis_label)
if selected_column == "fyllingsgrad":
    axis.yaxis.set_major_formatter(lambda value, _: f"{value:.0%}")
axis.grid(True, alpha=0.3)
if len(plot_data.columns) > 1:
    axis.legend(title="Data column")
figure.tight_layout()
st.pyplot(figure)
plt.close(figure)

if selected_column == "All columns":
    st.caption(
        "The national aggregate is shown. Columns are relative to their first "
        "displayed value so different scales can be compared."
    )