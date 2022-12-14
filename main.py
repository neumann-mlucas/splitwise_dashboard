import altair as alt
import pandas as pd
import streamlit as st

from charts import plot_one, plot_two
from utils import clean_csv

st.set_page_config(layout="wide")

df = None
with st.sidebar:
    st.title("Input Options")
    uploaded_file = st.file_uploader("CSV file")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)

        persons = df.columns[5:]
        currencies = df.iloc[:, 4].unique()

        person_opt = st.radio("Person", persons, index=0)
        currencies_opt = st.radio("Currency", currencies, index=0)

        df = clean_csv(df, currencies_opt, person_opt)

        start_date = st.date_input(
            "Start Date",
            value=min(df.index),
            min_value=min(df.index),
            max_value=max(df.index),
        )
        end_date = st.date_input(
            "End Date",
            value=max(df.index),
            min_value=min(df.index),
            max_value=max(df.index),
        )

st.title("Splitwise DashBoard")

if df is not None:
    po = plot_one(df.copy())
    st.subheader("Expenses x Time")
    st.altair_chart(po, use_container_width=True)

    pt = plot_two(df.copy())
    st.subheader("Expenses x Type")
    st.altair_chart(pt, use_container_width=True)

    st.subheader("DF describe")
    st.dataframe(df.describe(), use_container_width=True)

    st.subheader("Raw DF")
    st.dataframe(df, use_container_width=True)
