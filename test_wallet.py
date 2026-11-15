"""Run with: py -m unittest -v"""
import csv
import tempfile
import unittest
from pathlib import Path

from wallet_model import WalletStore, parse_amount


class WalletTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name)/"wallet.db"
        self.store = WalletStore(self.path, demo=False)

    def tearDown(self):
        self.store.close()
        self.temp.cleanup()

    def test_exact_amounts(self):
        self.assertEqual(parse_amount("0.29"), 29)
        self.assertEqual(parse_amount("1250.50"), 125050)
        for value in ("0", "-2", "NaN", "Infinity", "0.001", "abc", "", "1000000000"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_amount(value)

    def test_edit_delete_preserve_accounting(self):
        from datetime import date
        self.store.add_transaction('Allowance', 100000, 'Income')
        self.store.add_transaction('Books', -20000, 'Books & stationery')
        expense = self.store.transactions()[0]
        income = self.store.transactions()[1]
        self.store.update_transaction(expense['id'], 'Lab manual', -30000, 'Books & stationery', date.today().isoformat())
        self.assertEqual(self.store.balance, 70000)
        with self.assertRaises(ValueError):
            self.store.delete_transaction(income['id'])
        with self.assertRaises(ValueError):
            self.store.update_transaction(expense['id'], 'Too expensive', -100001, 'Other', date.today().isoformat())
        self.assertEqual(self.store.balance, 70000)
        self.store.delete_transaction(expense['id'])
        self.assertEqual(self.store.balance, 100000)

    def test_budget_daily_allowance_cannot_exceed_balance(self):
        self.store.add_transaction('Allowance', 10000, 'Income')
        self.store.set_setting('budget', 100000)
        result = self.store.budget_summary()
        self.assertEqual(result['daily'], 10000 // result['days'])
        self.store.add_transaction('Lunch', -9000, 'Food & drinks')
        self.store.set_setting('budget', 5000)
        self.assertEqual(self.store.budget_summary()['daily'], 0)

    def test_ledger_rejects_overdraft_and_persists(self):
        self.store.add_transaction("Salary", 100000, "Income")
        self.store.add_transaction("Coffee", -2999, "Food & drinks")
        self.assertEqual(self.store.balance, 97001)
        with self.assertRaises(ValueError):
            self.store.add_transaction("Too much", -97002, "Shopping")
        self.assertEqual(len(self.store.transactions()), 2)
        other = WalletStore(self.path)
        try:
            self.assertEqual(other.balance, 97001)
            self.assertEqual(other.monthly()[:2], (100000, 2999))
        finally:
            other.close()

    def test_search_and_filters(self):
        self.store.add_transaction("Salary", 100000, "Income")
        self.store.add_transaction("Coffee", -250, "Food & drinks")
        self.assertEqual(len(self.store.transactions("FOOD", "Expenses")), 1)
        self.assertEqual(len(self.store.transactions("Coffee", "Income")), 0)

    def test_card_validation_and_removal(self):
        for digits in ("123", "12345", "abcd", "１２３４"):
            with self.assertRaises(ValueError):
                self.store.add_card("Card", digits, "VISA", "#ED8C66")
        self.store.add_card("Card", "0123", "VISA", "#ED8C66")
        card = self.store.cards()[0]
        self.assertEqual(card['last4'], "0123")
        self.store.remove("cards", card['id'])
        self.assertEqual(len(self.store.cards()), 0)

    def test_new_wallet_contains_only_financial_tables(self):
        tables={r[0] for r in self.store.db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        self.assertEqual(tables,{'settings','cards','transactions'})

    def test_export_escapes_formulas_and_keeps_cents(self):
        self.store.add_transaction("=SUM(1,2)", 1029, "Income")
        path = Path(self.temp.name)/"out.csv"
        self.store.export_csv(path)
        with path.open(encoding="utf-8-sig", newline="") as file:
            rows = list(csv.reader(file))
        self.assertEqual(rows[1][1], "'=SUM(1,2)")
        self.assertEqual(rows[1][3], "10.29")

    def test_sample_data_seeds_only_once(self):
        other_path = Path(self.temp.name)/"sample.db"
        demo = WalletStore(other_path)
        balance, count = demo.balance, len(demo.transactions())
        demo.close()
        demo = WalletStore(other_path)
        try:
            self.assertEqual(demo.balance, balance)
            self.assertEqual(len(demo.transactions()), count)
            self.assertEqual(len(demo.cards()), 3)
            self.assertFalse(hasattr(demo,'cars'))
        finally:
            demo.close()


if __name__ == "__main__":
    unittest.main()
