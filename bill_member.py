# coding=utf-8
from load_readings import get_readings
import pandas as pd
from dateutil import parser

from tariff import BULB_TARIFF

ROUND_TO_DIGITS = 2

ALL = 'ALL'
CUMULATIVE = 'cumulative'
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.000Z"
ELECTRICITY = 'electricity'
READING_DATE = 'readingDate'
STANDING_CHARGE = 'standing_charge'
UNIT_RATE = 'unit_rate'


def data_flatten(data: dict):
    """ Take nested billing data and return as a list of dicts, with hierarchy of data flattened.
    """
    r = []
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


def do_calculation_electricity(units: float = None,
                               from_date: str = None,
                               to_date: str = None,
                               tarrif:dict=BULB_TARIFF):
    """
    returns in rounded (to nearest penny) pounds
    """
    standing_cost = calculate_standing_cost(ELECTRICITY, from_date, to_date, tarrif)
    units_cost = calculate_unit_cost(ELECTRICITY, units, tarrif)
    cost = units_cost + standing_cost
    return convert_to_rounded_pounds(cost)


def convert_to_rounded_pounds(cost):
    """ Given pence, return pounds and pence
    convert_to_rounded_pounds(123.4567)
    >>> 1.23
    """
    return round(cost / 100, ROUND_TO_DIGITS)


def calculate_unit_cost(energy_type, units, tarrif=BULB_TARIFF):
    units_cost = 0
    unit_rate = tarrif.get(energy_type, {}).get(UNIT_RATE)
    if units:
        units_cost = units * unit_rate
    return units_cost


def calculate_standing_cost(energy_type, from_date, to_date, tarrif=BULB_TARIFF):
    standing_rate = tarrif.get(energy_type, {}).get(STANDING_CHARGE)
    standing_cost = 0
    if from_date or to_date:
        fromdate, todate = parser.parse(from_date), parser.parse(to_date)
        days_charged = (todate - fromdate).days
        standing_cost = days_charged * standing_rate
    return standing_cost


def calculate_bill(member_id=None, account_id=None, bill_date=None):
    data = get_readings()
    df = pd.DataFrame(data_flatten(data))
    df2 = df.query(f'member_id == "{member_id}"')
    if account_id != ALL:
        df2 = df2.query(f'account_id == "{member_id}"')
    if bill_date:
        bill_date = parser.parse(bill_date).strftime(DATE_FORMAT)
        df2 = df2.query(f'{READING_DATE} <= "{bill_date}"')
    recent_items = df2[-2:]
    from_date, to_date = recent_items[READING_DATE].values[0], recent_items[READING_DATE].values[1]
    from_electric, to_electric = recent_items[CUMULATIVE].values[0], recent_items[CUMULATIVE].values[1]
    kwh = to_electric - from_electric
    amount = do_calculation_electricity(units=kwh,
                                        from_date=from_date,
                                        to_date=to_date)
    return amount, kwh


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
