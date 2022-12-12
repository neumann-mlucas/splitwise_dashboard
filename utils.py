import pandas as pd

STD_COLS = ("Date", "Text", "Type", "TotalCost", "Currency")


def standardize_columns(df):
    # in case columns names are not in English
    df.columns = [*STD_COLS, *df.columns[5:]]
    # clean rows with net balance
    df = df[df.TotalCost != " "]
    # assure column have the right type
    df["Date"] = pd.to_datetime(df.Date)
    return df


def unpivot_table(df: pd.DataFrame) -> pd.DataFrame:
    df = pd.melt(
        df,
        id_vars=STD_COLS,
        value_vars=df.columns[4:],
        var_name="Person",
        value_name="BalanceChange",
    )
    df["TotalCost"] = df.TotalCost.astype("float")
    df["BalanceChange"] = df.BalanceChange.astype("float")
    df["Cost"] = df.apply(
        calc_individual_cost,
        axis=1,
    )
    return df


def calc_individual_cost(row: pd.Series) -> float:
    "calculate individual expense for a given row entry"
    if row.BalanceChange == 0:
        return 0.0  # not included
    if row.BalanceChange < 0:
        return -1 * row.BalanceChange  # someone else paid
    else:
        return row.TotalCost - row.BalanceChange  # paid for the expense


def filter_values(
    df: pd.DataFrame, currency: str = "BRL", person: str = "Lucas Neumann"
) -> pd.DataFrame:
    df = df.drop(columns="Text")
    mask = (df.Currency == currency) & (df.Person == person) & (df.Cost != 0)
    return df[mask]


def clean_csv(df: pd.DataFrame, currency, person) -> pd.DataFrame:
    return (
        df.pipe(standardize_columns)
        .pipe(unpivot_table)
        .pipe(filter_values, currency=currency, person=person)
        .set_index("Date")
        .sort_index()
    )
