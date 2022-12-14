import altair as alt
import pandas as pd

DAYS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunda",
]


def plot_one(df: pd.DataFrame) -> alt.HConcatChart:
    "dashboard's first plot"
    timeseries = timeseries_chart(df)
    by_day = weekday_chart(df)
    by_type = type_barchart(df)

    return timeseries | (by_type & by_day)


def timeseries_chart(df: pd.DataFrame) -> alt.Chart:
    "time series of the last 4 weeks moving average + total expenses per week"

    source = df.Cost.resample("1W").sum().reset_index()
    source["cumCost"] = source.Cost.cumsum()

    gradient = alt.Gradient(
        gradient="linear",
        stops=[
            alt.GradientStop(color="white", offset=0),
            alt.GradientStop(color="darkgreen", offset=1),
        ],
        x1=1,
        x2=1,
        y1=1,
        y2=0,
    )

    mean = (
        alt.Chart(source)
        .mark_area(line={"color": "darkgreen"}, color=gradient)
        .transform_window(
            monthly_rolling_mean="sum(Cost)",
            frame=[-4, 0],
        )
        .encode(
            x="Date:T",
            y=alt.Y("monthly_rolling_mean:Q", title="Cost"),
            tooltip=["Date:T", "monthly_rolling_mean:Q"],
        )
    )

    by_week = (
        alt.Chart(source)
        .mark_bar()
        .encode(
            x="Date:T", y="Cost:Q", color=alt.value("red"), tooltip=["Date:T", "Cost:Q"]
        )
    )

    return (mean + by_week).properties(height=660, title="Expenses Time Series")


def type_barchart(df: pd.DataFrame) -> alt.Chart:
    "cost per month broken into expense types"

    df["Total"] = df.Cost.cumsum()
    source = (
        df.groupby([pd.Grouper(freq="1M"), "Type"])
        .Cost.sum()
        .unstack("Type", fill_value=0)
    )
    source = pd.melt(
        source.reset_index(),
        id_vars="Date",
        value_name="Cost",
    )

    return (
        alt.Chart(source)
        .mark_bar()
        .encode(
            y=alt.Y("Date:T", timeUnit="yearmonth", sort="descending", title=None),
            x=alt.X("sum(Cost)"),
            color="Type:N",
            tooltip=["Date:T", "Type:N", "Cost:Q"],
        )
    ).properties(height=300, title="Montly Expenses")


def weekday_chart(df: pd.DataFrame) -> alt.Chart:
    "mean cost per day of the week"
    source = df.reset_index()
    source["dayname"] = source.Date.dt.day_name()

    return (
        alt.Chart(source)
        .mark_bar()
        .encode(
            x="mean(Cost):Q",
            y=alt.Y("dayname:N", sort=DAYS, title=None),
            color=alt.value("red"),
            tooltip=["dayname:N", "mean(Cost):Q"],
        )
    ).properties(height=300, title="Avg Expenses by Day of Week")


def plot_two(df: pd.DataFrame) -> alt.HConcatChart:
    "dashboard's second plot"
    source = df.reset_index()
    q = source["Cost"].quantile(0.99)
    source = source[source["Cost"] < q]

    brush = alt.selection(type="interval", resolve="global")
    legend = alt.selection_multi(fields=["Type"], bind="legend")

    base = alt.Chart(source)
    hists = hist_cost(base, brush, legend) & hist_type(base, brush, legend)
    scatter = scatter_chart(base, brush, legend)

    return scatter | hists


def hist_cost(base, brush, legend) -> alt.Chart:
    "histogram of expense costs"

    base = (
        base.mark_bar().encode(
            x=alt.X("TotalCost:Q", bin=alt.Bin(maxbins=20), title=None),
            y=alt.Y("sum(TotalCost):Q", title=None),
            tooltip=["Type", "sum(TotalCost)"],
        )
    ).properties(height=300, width=300, title="Expenses Value Histogram")

    bg = base.encode(color=alt.value("#ddd"))
    fg = base.add_selection(brush).transform_filter(brush).transform_filter(legend)

    return bg + fg


def hist_type(base, brush, legend) -> alt.Chart:
    "histogram of expenses types"

    base = (
        base.mark_bar().encode(
            x=alt.X("Type:N", title=None),
            y=alt.Y("sum(TotalCost):Q", title=None),
            tooltip=["Type", "sum(TotalCost)"],
        )
    ).properties(height=300, width=300, title="Expenses Type Histogram")

    bg = base.encode(color=alt.value("grey"))
    fg = (
        base.encode(color="Type:N")
        .add_selection(brush)
        .transform_filter(brush)
        .transform_filter(legend)
    )

    return bg + fg


def scatter_chart(base, brush, legend) -> alt.Chart:
    "scatter plot of time x cost of each expense"

    return (
        base.mark_circle()
        .encode(
            x="Date:T",
            y="TotalCost:Q",
            size=alt.Size("TotalCost:Q", legend=None),
            color=alt.condition(brush, "Type:N", alt.value("#ddd")),
            opacity=alt.condition(legend, alt.value(1.0), alt.value(0.2)),
            tooltip=["Date:T", "Type", "TotalCost", "Cost", "Text"],
        )
        .add_selection(brush)
        .add_selection(legend)
    ).properties(height=660, title="expenses scatter plot")
