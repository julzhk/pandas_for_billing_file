# coding=utf-8
from typing import List, Any

import pandas as pd
from dateutil import parser

from load_readings import get_readings
from tariff import BULB_TARIFF

ROUND_TO_DIGITS = 2
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.000Z"

ALL = 'ALL'
CUMULATIVE = 'cumulative'
ELECTRICITY = 'electricity'
GAS = 'gas'
READING_DATE = 'readingDate'
STANDING_CHARGE = 'standing_charge'
UNIT_RATE = 'unit_rate'


def data_flatten(data: dict) -> List[dict]:
    """ Take nested billing data and return as a list of dicts, with hierarchy of data flattened.
    """
    r: List[dict] = []
    for member_id in data:
        for accounts in data[member_id]:
            for account_count, account_id in enumerate(accounts):
                for reading_count, reading_data in enumerate(data[member_id][account_count][account_id]):
                    for reading_type_count, reading_type in enumerate(reading_data):
                        for reading in (reading_data[reading_type]):
                            reading['account_id'] = account_id
                            reading['member_id'] = member_id
                            reading['type'] = reading_type
                            r.append(reading)
    return r


def do_calculation(units: float = None,
                   from_date: str = None,
                   to_date: str = None,
                   tarriff: dict = BULB_TARIFF) -> float:
    """
    returns in rounded (to nearest penny) pounds
    """
    cost :float = 0
    standing_cost: float = calculate_standing_cost(energy_type=ELECTRICITY,
                                                   from_date=from_date,
                                                   to_date=to_date,
                                                   tarriff=tarriff
                                                   )
    units_cost = calculate_unit_cost(energy_type=ELECTRICITY,
                                     units=units,
                                     tarriff=tarriff
                                     )
    cost += units_cost + standing_cost
    return convert_to_rounded_pounds(cost)


def convert_to_rounded_pounds(cost):
    """ Given pence, return pounds and pence
    convert_to_rounded_pounds(123.4567)
    >>> 1.23
    """
    return round(cost / 100, ROUND_TO_DIGITS)


def calculate_unit_cost(energy_type, units, tarriff=BULB_TARIFF):
    """
    @energy_type:'gas'|'electricity'
    @units:float
    @tariff:dict
    """
    units_cost: float = 0
    unit_rate: float = tarriff.get(energy_type, {}).get(UNIT_RATE, 0)
    if units:
        units_cost = units * unit_rate
    return units_cost


def calculate_standing_cost(energy_type: str, from_date: str, to_date: str, tarriff: dict = BULB_TARIFF) -> float:
    standing_rate: float = tarriff.get(energy_type, {}).get(STANDING_CHARGE, 0)
    standing_cost: float = 0
    if from_date and to_date:
        fromdate, todate = parser.parse(from_date), parser.parse(to_date)
        days_charged : int = (todate - fromdate).days
        standing_cost: float = (days_charged * standing_rate)
    return standing_cost


def calculate_bill(member_id=None, account_id=None, bill_date=None):
    data = get_readings()
    df = pd.DataFrame(data_flatten(data))
    df = filter_df_by_member_id(df, member_id)
    df = filter_df_by_account_id(df, account_id)
    df = filter_df_by_bill_date(df, bill_date)
    recent_items = filter_df_recent_items(df, 2)
    from_date, to_date = extract_df_by_column(recent_items=recent_items,
                                              column_label=READING_DATE)
    prev_electric_reading, bill_date_electric_reading = extract_df_by_column(recent_items=recent_items,
                                                                             column_label=CUMULATIVE)
    kwh = bill_date_electric_reading - prev_electric_reading
    amount = do_calculation(units=kwh,
                            from_date=from_date,
                            to_date=to_date)
    return amount, kwh


def extract_df_by_column(recent_items, column_label):
    return (recent_items[column_label].values[0],
            recent_items[column_label].values[1])


def filter_df_recent_items(df2, recent_item_count=2):
    return df2[-recent_item_count:]


def filter_df_by_bill_date(df2, bill_date):
    if bill_date:
        bill_date = parser.parse(bill_date).strftime(DATE_FORMAT)
        df2 = df2.query(f'{READING_DATE} <= "{bill_date}"')
    return df2


def filter_df_by_account_id(df2, account_id):
    if account_id != ALL:
        df2 = df2.query(f'account_id == "{account_id}"')
    return df2


def filter_df_by_member_id(df, member_id):
    return df.query(f'member_id == "{member_id}"')


def calculate_and_print_bill(member_id, account, bill_date):
    """Calculate the bill and then print it to screen.
    Account is an optional argument - I could bill for one account or many.
    There's no need to refactor this function."""
    member_id = member_id or 'member-123'
    bill_date = bill_date or '2017-08-31'
    account = account or 'ALL'
    amount, kwh = calculate_bill(member_id, account, bill_date)
    print('Hello {member}!'.format(member=member_id))
    print('Your bill for {account} on {date} is £{amount}'.format(
        account=account,
        date=bill_date,
        amount=amount))
    print('based on {kwh}kWh of usage in the last month'.format(kwh=kwh))
