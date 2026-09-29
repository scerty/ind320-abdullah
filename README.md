# IND320 Reservoir Data Project

This repository contains Part 1 of an IND320 project. It includes a Jupyter
Notebook for exploring reservoir data and a small Streamlit application for
viewing and plotting the same data.

## Setup

Create and activate a Python environment, then install the required packages:

```text
pip install -r requirements.txt
```

The real course file named `reservoirs.csv` is included in the project root,
next to `app.py`. If the file is replaced later, keep the same filename and
location so the notebook and Streamlit pages can find it.

Run the application locally with:

```text
streamlit run app.py
```

## Project structure

```text
app.py                  Streamlit home page
pages/2_Data.py         Imported data and row-oriented series table
pages/3_Plot.py         Interactive reservoir plot
pages/4_About.py        Project information placeholder
ind320_part1.ipynb      Part 1 analysis notebook
requirements.txt        Python dependencies
reservoirs.csv          Required local course data file
```

The data-loading functions are isolated so the project can later be extended
to use MongoDB for Part 2.

GitHub repository: https://github.com/scerty/ind320-abdullah

Streamlit deployment: **To be added after deployment**

`https://YOURPROJECT.streamlit.app/`