""" Methods to add UTC datetimes"""
import pandas as pd


def add_utc_datetime(df: pd.DataFrame) ->  pd.DataFrame:
    """
    Make 'settlement_period_start_utc' from 'Settlement Day' and 'Settlement Period'

    settlement_period_start_utc is the datetime with utc timezone of the settle period

    :param df: datafrome containing 'Settlement Day' and 'Settlement Period'
    :return: dataframe with
    """

    # only works for "Settlement Day" and "Settlement Period" right now
    if not ("Settlement Day" in df.columns and "Settlement Period" in df.columns):
        return df

    # get start of day in UTC
    settlement_day_start = pd.to_datetime(df["Settlement Day"]).dt.tz_localize(tz="Europe/London")
    settlement_day_start_utc = settlement_day_start.dt.tz_convert(tz="UTC")

    # add 30 minutes * `Settlement Period` to start of day UTC
    df["settlement_period_start_utc"] = settlement_day_start_utc + pd.to_timedelta(
        30 * (df["Settlement Period"] - 1), "T"
    )

    return df
