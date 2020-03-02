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

    def test_calculation(self):
        result = do_calculation(units=0, from_date= '31-11-01', to_date='01-12-01')
        self.assertEqual(result,123)

if __name__ == '__main__':
    unittest.main()
