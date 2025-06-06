import unittest

from tvscreener import ForexScreener, TimeInterval, ForexField, FilterOperator
from tvscreener.field import Region


class TestForexScreener(unittest.TestCase):

    def test_len(self):
        fs = ForexScreener()
        df = fs.get()
        self.assertGreaterEqual(len(df), 100)

    def test_time_interval(self):
        fs = ForexScreener()
        df = fs.get(time_interval=TimeInterval.FOUR_HOURS)
        self.assertGreaterEqual(len(df), 100)

    def test_region(self):
        fs = ForexScreener()
        fs.add_filter(ForexField.REGION, FilterOperator.EQUAL, Region.AFRICA)
        df = fs.get()
        self.assertGreaterEqual(len(df), 30)

        self.assertTrue("FX_IDC:GHSNGN" in df["Symbol"].values)
        self.assertTrue("GHSNGN" in df["Name"].values)
