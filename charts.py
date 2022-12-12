import altair as alt
import pandas as pd


def simple_timeseries(df):
    source = df[["BalanceChange", "Cost"]].cumsum().reset_index()
    a = (
        alt.Chart(source)
        .mark_line()
        .encode(x="Date:T", y="Cost:Q", color=alt.value("red"))
    )
    b = alt.Chart(source).mark_line().encode(x="Date:T", y="BalanceChange:Q")
    return a + b


def area_chart(df):
    df["Total"] = df.Cost.cumsum()
    source = (
        df.groupby([pd.Grouper(freq="1D"), "Type"])
        .Cost.sum()
        .unstack("Type", fill_value=0)
        .cumsum()
    )
    source = pd.melt(
        source.reset_index(),
        id_vars="Date",
        value_name="Total Expense",
    )

    return (
        alt.Chart(source)
        .mark_area()
        .encode(
            x="Date:T", y=alt.Y("Total Expense:Q", stack="normalize"), color="Type:N"
        )
    )


def bar_by_type(df):
    source = df.groupby("Type").sum().reset_index()
    return (
        alt.Chart(source)
        .mark_bar()
        .encode(
            y="Cost:Q",
            x="Type:N",
            color=alt.Color("Type:N", legend=None),
        )
    )


def bar_by_date(df):
    source = df.Cost.resample("1W").sum().reset_index()
    return (
        alt.Chart(source)
        .mark_bar()
        .encode(
            y="Cost:Q",
            x="Date:T",
        )
    )
