import tempfile
import unittest
from pathlib import Path
from tkinter import ttk
from main import WalletApp
from wallet_model import WalletStore


class BasicAppTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.app = WalletApp(WalletStore(Path(self.temp.name) / 'test.db', demo=False))
        self.app.update()

    def tearDown(self):
        self.app.close()
        self.temp.cleanup()

    def test_balance_search_and_cards(self):
        self.app.store.add_transaction('Salary', 100000, 'Income')
        self.app.store.add_transaction('Coffee', -25000, 'Food & drinks')
        self.app.store.add_card('Everyday', '1234', 'VISA', '#3457b1')
        self.app.refresh()
        self.assertEqual(self.app.stats[0].cget('text'), '₹750.00')
        self.assertEqual(len(self.app.transactions.get_children()), 2)
        self.assertEqual(len(self.app.cards.get_children()), 1)
        self.app.query.set('coffee')
        self.assertEqual(len(self.app.transactions.get_children()), 1)
        self.app.kind.set('Income')
        self.app.refresh_transactions()
        self.assertEqual(len(self.app.transactions.get_children()), 0)

    def test_income_form_saves_entry(self):
        dialog = self.app.transaction_form(True)
        self.app.update()
        frame = dialog.winfo_children()[0]
        entries = [child for child in frame.winfo_children() if isinstance(child, ttk.Entry)]
        entries[0].insert(0, 'Pocket money')
        entries[1].insert(0, '100.25')
        actions = frame.winfo_children()[-1]
        next(button for button in actions.winfo_children() if button.cget('text') == 'Save').invoke()
        self.app.update()
        self.assertEqual(self.app.store.balance, 10025)
        self.assertEqual(len(self.app.transactions.get_children()), 1)


if __name__ == '__main__':
    unittest.main()
