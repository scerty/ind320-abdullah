"""Entry point for the IND320 Part 1 Streamlit application."""

import streamlit as st


st.set_page_config(page_title="IND320 Project", page_icon=":bar_chart:", layout="wide")

st.title("IND320 Reservoir Data Project")
st.write(
    "This Streamlit application is the starting point for the IND320 project. "
    "Use the pages in the sidebar to inspect and plot the reservoir data."
)

st.sidebar.title("Project navigation")
st.sidebar.page_link("app.py", label="Home", icon=":material/home:")
st.sidebar.page_link("pages/2_Data.py", label="Data", icon=":material/table_view:")
st.sidebar.page_link("pages/3_Plot.py", label="Plot", icon=":material/show_chart:")
st.sidebar.page_link("pages/4_About.py", label="About", icon=":material/info:")

st.subheader("Part 1")
st.write(
    "Part 1 uses a local `reservoirs.csv` file. The data-loading functions are "
    "kept separate so the project can later be extended to use MongoDB."
)