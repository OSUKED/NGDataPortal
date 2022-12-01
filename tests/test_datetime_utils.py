import pandas as pd
from datetime import datetime, timedelta, timezone

from NGDataPortal.datetime_utils import add_utc_datetime
from NGDataPortal.NGDataPortal import Wrapper


def test_add_utc_datetime_winter():

    df = pd.DataFrame(
        columns=["Settlement Day", "Settlement Period"],
        data=[[datetime(2022, 1, 1), 1], [datetime(2022, 1, 1), 2]],
    )

    df = add_utc_datetime(df)

    assert df.iloc[0].settlement_period_start_utc == datetime(2022, 1, 1, tzinfo=timezone.utc)
    assert df.iloc[1].settlement_period_start_utc == datetime(
        2022, 1, 1, 0, 30, tzinfo=timezone.utc
    )


def test_add_utc_datetime_summer():

    df = pd.DataFrame(
        columns=["Settlement Day", "Settlement Period"],
        data=[[datetime(2022, 7, 1), 1], [datetime(2022, 7, 1), 2]],
    )

    df = add_utc_datetime(df)

    assert df.iloc[0].settlement_period_start_utc == datetime(2022, 6, 30, 23, tzinfo=timezone.utc)
    assert df.iloc[1].settlement_period_start_utc == datetime(
        2022, 6, 30, 23, 30, tzinfo=timezone.utc
    )


def test_add_utc_datetime_clock_change_spring():
    start_date = "2021-03-28"
    end_date = "2021-03-28"
    dt_col = "Settlement Day"

    stream = "current-balancing-services-use-of-system-bsuos-data"
    wrapper = Wrapper(stream=stream)

    df = wrapper.query_API(start_date=start_date, end_date=end_date, dt_col=dt_col)

    assert len(df) == 46

    assert df.iloc[0].settlement_period_start_utc == datetime(2021, 3, 28, tzinfo=timezone.utc)
    assert df.iloc[1].settlement_period_start_utc == datetime(
        2021, 3, 28, 0, 30, tzinfo=timezone.utc
    )
    assert df.iloc[-1].settlement_period_start_utc == datetime(
        2021, 3, 28, 22, 30, tzinfo=timezone.utc
    )


def test_add_utc_datetime_clock_change_autumn():
    start_date = "2020-10-25"
    end_date = "2020-10-25"
    dt_col = "Settlement Day"

    stream = "current-balancing-services-use-of-system-bsuos-data"
    wrapper = Wrapper(stream=stream)

    df = wrapper.query_API(start_date=start_date, end_date=end_date, dt_col=dt_col)

    assert len(df) == 50

    assert df.iloc[0].settlement_period_start_utc == datetime(2020, 10, 24, 23, tzinfo=timezone.utc)
    assert df.iloc[1].settlement_period_start_utc == datetime(
        2020, 10, 24, 23, 30, tzinfo=timezone.utc
    )
    assert df.iloc[-1].settlement_period_start_utc == datetime(
        2020, 10, 25, 23, 30, tzinfo=timezone.utc
    )
