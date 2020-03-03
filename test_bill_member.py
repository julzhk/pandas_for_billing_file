import datetime
import unittest
from bill_member import calculate_bill, data_flatten, do_calculation


class TestBillMember(unittest.TestCase):

    def test_calculate_bill_for_august(self):
        amount, kwh = calculate_bill(member_id='member-123',
                                     account_id='ALL',
                                     bill_date='2017-08-31')
        self.assertEqual(amount, 27.57)
        self.assertEqual(kwh, 167)


class TestReadSourceData(unittest.TestCase):
    def test_flatten(self):
        testdata = {
            "member-123": [
                {
                    "account-abc": [
                        {
                            "electricity": [
                                {
                                    "cumulative": 20600,
                                    "readingDate": "2018-04-29T00:00:00.000Z",
                                    "unit": "kWh"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        flattened_data = data_flatten(testdata)[0]
        self.assertEqual(flattened_data['member_id'], 'member-123')
        self.assertDictEqual(flattened_data, {
            'cumulative': 20600,
            'readingDate': '2018-04-29T00:00:00.000Z',
            'unit': 'kWh',
            'account_id': 'account-abc',
            'member_id': 'member-123',
            'type': 'electricity'
        })

    def test_calculation_units(self):
        result = do_calculation(units=10, tarriff={
            "electricity": {
                "unit_rate": 10,  # pence per kWh
                "standing_charge": 0  # fixed daily charge in pence
            }
        })
        self.assertEqual(result, 1)

    def test_calculation_standing(self):
        result = do_calculation(units=167,
                                from_date='2017-07-31T00:00:00.000Z',
                                to_date='2017-08-31T00:00:00.000Z')
        self.assertEqual(result, 27.57)

    def test_calculation_standing_and_units(self):
        result = do_calculation(from_date='2017-08-29',
                                to_date='2017-08-31',
                                tarriff={
                                                "electricity": {
                                                    "unit_rate": 0,  # pence per kWh
                                                    "standing_charge": 100  # fixed daily charge in pence
                                                }
                                            })
        self.assertEqual(result, 2)


if __name__ == '__main__':
    unittest.main()
