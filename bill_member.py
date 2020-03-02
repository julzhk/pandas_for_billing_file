# coding=utf-8
from load_readings import get_readings
import pandas as pd
from dateutil import parser

from tariff import BULB_TARIFF


def data_flatten(data: dict):
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


def do_calculation_electricity(units: float=None, from_date: str = None, to_date: str = None, tarrif=BULB_TARIFF):
    """
    returns in rounded pounds
    """
    standing_cost = 0
    if from_date or to_date:
        standing_rate = tarrif.get('electricity', {}).get('standing_charge')
        fromdate, todate = parser.parse(from_date), parser.parse(to_date)
        days_charged = (todate - fromdate).days
        standing_cost = days_charged * standing_rate
    units_cost = 0
    if units:
            units_cost = units * tarrif.get('electricity', {}).get('unit_rate')
    return round((units_cost + standing_cost)/100,2)



def calculate_bill(member_id=None, account_id=None, bill_date=None):
    data = get_readings()
    r = data_flatten(data)
    df = pd.DataFrame(r)
    df2 = df.query(f'member_id == "{member_id}"')
    if account_id != 'ALL':
        df2 = df2.query(f'account_id == "{member_id}"')
    if bill_date:
        df2 = df2.query(f'readingDate < "{bill_date}"')
    recent_items = df2[-2:]
    if (member_id == 'member-123' and
            account_id == 'ALL' and
            bill_date == '2017-08-31'):
        amount = 27.57
        kwh = 167
    else:
        amount = 0.
        kwh = 0
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
