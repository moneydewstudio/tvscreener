import io
import unittest
from unittest.mock import patch

import pandas as pd

from tvscreener import StockScreener, TimeInterval, MalformedRequestException, \
    ExtraFilter, FilterOperator, StockField
from tvscreener.field import SymbolType, Market, SubMarket, Country, Exchange


class TestScreener(unittest.TestCase):

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_stdout(self, mock_stdout):
        ss = StockScreener()
        ss.get(print_request=True)
        self.assertIn("filter", mock_stdout.getvalue())

    def test_malformed_request(self):
        ss = StockScreener()
        ss.add_filter(StockField.TYPE, FilterOperator.ABOVE_OR_EQUAL, "test")
        with self.assertRaises(MalformedRequestException):
            ss.get()

    def test_range(self):
        ss = StockScreener()
        df = ss.get()
        self.assertGreaterEqual(len(df), 100)

    def test_time_interval(self):
        ss = StockScreener()
        df = ss.get(time_interval=TimeInterval.FOUR_HOURS)
        self.assertGreaterEqual(len(df), 100)

    def test_search(self):
        ss = StockScreener()
        ss.set_symbol_types(SymbolType.COMMON_STOCK)
        ss.search('AA')
        df = ss.get()
        self.assertGreaterEqual(len(df), 10)

        self.assertTrue(df["Symbol"].str.contains("AA").any())
        self.assertTrue(df["Name"].str.contains("AA", case=False).any())

    def test_column_order(self):
        ss = StockScreener()
        df = ss.get()

        self.assertEqual(df.columns[0], "Symbol")
        self.assertEqual(df.columns[1], "Name")
        self.assertEqual(df.columns[2], "Description")

        self.assertTrue("NASDAQ:AAPL" in df["Symbol"].values)
        self.assertTrue("AAPL" in df["Name"].values)

    def test_not_multiindex(self):
        ss = StockScreener()
        df = ss.get()
        self.assertIsInstance(df.index, pd.Index)

        self.assertEqual("Symbol", df.columns[0])
        self.assertEqual("Name", df.columns[1])
        self.assertEqual("Description", df.columns[2])

        self.assertTrue("NASDAQ:AAPL" in df["Symbol"].values)
        self.assertTrue("AAPL" in df["Name"].values)

    def test_multiindex(self):
        ss = StockScreener()
        df = ss.get()
        df.set_technical_columns()
        self.assertNotIsInstance(df.index, pd.MultiIndex)

        self.assertEqual(("symbol", "Symbol"), df.columns[0])
        self.assertEqual(("name", "Name"), df.columns[1])
        self.assertEqual(("description", "Description"), df.columns[2])

        self.assertTrue("NASDAQ:AAPL" in df[("symbol", "Symbol")].values)
        self.assertTrue("AAPL" in df[("name", "Name")].values)

    def test_technical_index(self):
        ss = StockScreener()
        df = ss.get()
        df.set_technical_columns(only=True)
        self.assertIsInstance(df.index, pd.Index)

        self.assertEqual(df.columns[0], "symbol")
        self.assertEqual(df.columns[1], "name")
        self.assertEqual(df.columns[2], "description")

        self.assertTrue("NASDAQ:AAPL" in df["symbol"].values)
        self.assertTrue("AAPL" in df["name"].values)

    def test_primary_filter(self):
        ss = StockScreener()
        ss.add_filter(ExtraFilter.PRIMARY, FilterOperator.EQUAL, True)
        df = ss.get()
        self.assertGreaterEqual(len(df), 100)

        self.assertTrue("NASDAQ:AAPL" in df["Symbol"].values)
        self.assertTrue("AAPL" in df["Name"].values)

    def test_market(self):
        ss = StockScreener()
        ss.set_markets(Market.ARGENTINA)
        df = ss.get()
        self.assertGreaterEqual(len(df), 100)

        # WARNING: Order is not guaranteed
        self.assertTrue(df["Symbol"].str.startswith("BCBA:").any())
        # self.assertTrue("AA" in df["Name"].values) # Symbol check is more reliable

    def test_submarket(self):
        ss = StockScreener()
        ss.add_filter(StockField.SUBMARKET, FilterOperator.EQUAL, SubMarket.OTCQB)
        df = ss.get()
        self.assertGreaterEqual(len(df), 100)

        self.assertTrue("OTC:PLDGP" in df["Symbol"].values)
        self.assertTrue("PLDGP" in df["Name"].values)

    def test_submarket_pink(self):
        ss = StockScreener()
        ss.add_filter(StockField.SUBMARKET, FilterOperator.EQUAL, SubMarket.PINK)
        df = ss.get()
        self.assertGreaterEqual(len(df), 100)

        # WARNING: Order is not guaranteed
        self.assertTrue(df["Symbol"].str.contains("OTC:LVM").any())
        self.assertTrue(df[df["Symbol"].str.contains("OTC:LVM", na=False)]["Name"].str.contains("LVM", case=False).any())

    def test_country(self):
        ss = StockScreener()
        ss.add_filter(StockField.COUNTRY, FilterOperator.EQUAL, Country.ARGENTINA)
        df = ss.get()
        self.assertGreaterEqual(len(df), 10)

        self.assertTrue("NYSE:YPF" in df["Symbol"].values)
        self.assertTrue("YPF" in df["Name"].values)

    def test_countries(self):
        ss = StockScreener()
        ss.add_filter(StockField.COUNTRY, FilterOperator.EQUAL, Country.ARGENTINA)
        ss.add_filter(StockField.COUNTRY, FilterOperator.EQUAL, Country.BERMUDA)
        df = ss.get()
        self.assertGreaterEqual(len(df), 50)

        # WARNING: Order is not guaranteed
        # self.assertEqual("NASDAQ:ACGL", df.loc[0, "Symbol"])
        # self.assertEqual("ACGL", df.loc[0, "Name"])

    def test_exchange(self):
        ss = StockScreener()
        ss.add_filter(StockField.EXCHANGE, FilterOperator.EQUAL, Exchange.NYSE_ARCA)
        df = ss.get()
        self.assertGreaterEqual(len(df), 100)

        self.assertTrue(df["Symbol"].str.startswith("AMEX:").any())
        # self.assertTrue("LNG" in df["Name"].values) # Name can be less stable

    def test_current_trading_day(self):
        ss = StockScreener()
        ss.add_filter(ExtraFilter.CURRENT_TRADING_DAY, FilterOperator.EQUAL, True)
        df = ss.get()
        self.assertGreaterEqual(len(df), 100)

        self.assertTrue("NASDAQ:AAPL" in df["Symbol"].values)
        self.assertTrue("AAPL" in df["Name"].values)
