"""Exercise the Tkinter controls with disposable, in-window demo values."""
import unittest
from decimal import Decimal
from unittest.mock import patch
from tkinter import ttk
from main import WalletApp


class GuiTests(unittest.TestCase):
    def setUp(self):
        self.app = WalletApp()
        self.errors = []
        self.app.report_callback_exception = lambda *args: self.errors.append(args)
        self.app.update()

    def tearDown(self):
        self.app.destroy()
        self.assertEqual(self.errors, [], 'Tkinter callback raised an exception')

    def submit(self, dialog, values):
        self.app.update()
        frame = dialog.winfo_children()[0]
        fields = [w for w in frame.winfo_children() if isinstance(w, ttk.Entry)]
        for field, value in zip(fields, values):
            if isinstance(field, ttk.Combobox):
                field.set(value)
            else:
                field.delete(0, 'end')
                field.insert(0, value)
        actions = frame.winfo_children()[-1]
        next(w for w in actions.winfo_children() if w.cget('text') == 'Save').invoke()
        self.app.update()

    def test_startup_tabs_and_search(self):
        self.assertEqual(self.app.stats[0].cget('text'), '₹4,350.00')
        self.assertEqual(len(self.app.tabs.tabs()), 3)
        for tab in self.app.tabs.tabs():
            self.app.tabs.select(tab)
            self.app.update()
        self.assertTrue(self.app.chart.find_all())
        self.app.query.set('lab')
        self.assertEqual(len(self.app.transactions.get_children()), 1)
        self.app.kind.set('Income')
        self.app.refresh_transactions()
        self.assertEqual(len(self.app.transactions.get_children()), 0)

    def test_income_and_expense_forms(self):
        self.submit(self.app.transaction_form(True), ['Allowance', '100.25'])
        self.submit(self.app.transaction_form(False), ['Coffee', '25.50', 'Food & drinks'])
        self.assertEqual(self.app.balance, Decimal('4424.75'))
        self.assertEqual(len(self.app.transactions.get_children()), 6)

    def test_invalid_forms_keep_values_unchanged(self):
        original = self.app.balance
        for value in ('abc', 'NaN', 'Infinity', '-5', '0', '1.001', '1000000000'):
            dialog = self.app.transaction_form(False)
            self.submit(dialog, ['Invalid', value, 'Other'])
            self.assertTrue(dialog.winfo_exists())
            self.assertEqual(self.app.balance, original)
            dialog.destroy()
        dialog = self.app.transaction_form(False)
        self.submit(dialog, ['Too much', '5000', 'Other'])
        self.assertTrue(dialog.winfo_exists())
        dialog.destroy()

    def test_edit_delete_and_confirmation(self):
        self.app.transactions.selection_set('3')
        self.submit(self.app.edit_transaction(), ['Lab manual', '350', self.app.entries[2]['day'], 'Books & stationery'])
        self.assertEqual(self.app.balance, Decimal('4400'))
        self.app.transactions.selection_set('3')
        with patch('main.messagebox.askyesno', return_value=False):
            self.app.delete_transaction()
        self.assertEqual(len(self.app.entries), 4)
        with patch('main.messagebox.askyesno', return_value=True):
            self.app.delete_transaction()
        self.assertEqual(self.app.balance, Decimal('4750'))
        self.app.transactions.selection_set('1')
        with patch('main.messagebox.askyesno', return_value=True), patch('main.messagebox.showerror') as error:
            self.app.delete_transaction()
            error.assert_called_once()
        self.assertEqual(self.app.balance, Decimal('4750'))

    def test_card_and_budget_forms(self):
        dialog = self.app.card_form()
        self.submit(dialog, ['Test', 'abc', 'VISA'])
        self.assertTrue(dialog.winfo_exists())
        self.submit(dialog, ['Test', '9876', 'RuPay'])
        self.assertEqual(len(self.app.cards.get_children()), 2)
        self.app.cards.selection_set('2')
        with patch('main.messagebox.askyesno', return_value=True):
            self.app.remove_card()
        self.assertEqual(len(self.app.cards.get_children()), 1)
        self.submit(self.app.budget_form(), ['2000'])
        self.assertIn('₹2,000.00', self.app.pace_text.cget('text'))

    def test_empty_views_and_new_window_reset(self):
        self.app.entries.clear()
        self.app.card_items.clear()
        self.app.refresh()
        self.assertEqual(self.app.stats[0].cget('text'), '₹0.00')
        self.assertFalse(self.app.transactions.get_children())
        self.app.destroy()
        self.app = WalletApp()
        self.app.update()
        self.assertEqual(self.app.balance, Decimal('4350'))
        self.assertEqual(len(self.app.cards.get_children()), 1)

    def test_cancel_and_selection_prompts(self):
        dialog = self.app.transaction_form(True)
        frame = dialog.winfo_children()[0]
        actions = frame.winfo_children()[-1]
        next(w for w in actions.winfo_children() if w.cget('text') == 'Cancel').invoke()
        self.assertEqual(len(self.app.entries), 4)
        with patch('main.messagebox.showinfo') as info:
            self.app.edit_transaction()
            self.app.remove_card()
            self.assertEqual(info.call_count, 2)


if __name__ == '__main__':
    unittest.main()
