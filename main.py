import altair as alt
import pandas as pd
import streamlit as st

from charts import *
from utils import clean_csv

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
    bd = bar_by_date(df)
    st.subheader("Expenses by Week")
    st.altair_chart(bd, use_container_width=True)

    bt = bar_by_type(df)
    st.subheader("Expenses by Type")
    st.altair_chart(bt, use_container_width=True)

    ac = area_chart(df)
    st.subheader("Percentage of Expenses by Type")
    st.altair_chart(ac, use_container_width=True)
