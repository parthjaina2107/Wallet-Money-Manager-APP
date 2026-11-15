"""Basic wallet manager, using only Python's standard library."""
import argparse
import os
import tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox, filedialog
from wallet_model import WalletStore, CATEGORIES, parse_amount, money


class WalletApp(tk.Tk):
    def __init__(self, store):
        super().__init__()
        self.store = store
        self.title('Wallet — Money Manager APP')
        self.geometry('1050x720')
        self.minsize(850, 590)
        self.configure(bg='#f2f4f8')
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TFrame', background='#f2f4f8')
        style.configure('TLabel', background='#f2f4f8', foreground='#243047', font=('Segoe UI', 11))
        style.configure('TButton', font=('Segoe UI', 10), padding=9)
        style.configure('Treeview', rowheight=33, font=('Segoe UI', 10), background='white', fieldbackground='white')
        style.configure('Treeview.Heading', font=('Segoe UI', 10, 'bold'), padding=8)
        outer = ttk.Frame(self, padding=24)
        outer.pack(fill='both', expand=True)
        header = ttk.Frame(outer)
        header.pack(fill='x')
        ttk.Label(header, text='My Wallet', font=('Segoe UI', 26, 'bold')).pack(side='left')
        ttk.Button(header, text='+ Income', command=lambda: self.transaction_form(True)).pack(side='right', padx=(8, 0))
        ttk.Button(header, text='+ Expense', command=lambda: self.transaction_form(False)).pack(side='right')
        summary = ttk.Frame(outer, padding=(0, 20))
        summary.pack(fill='x')
        self.stats = []
        for title, color in [('Available balance', '#3457b1'), ('Income this month', '#21775c'), ('Expenses this month', '#b85151')]:
            panel = tk.Frame(summary, bg='white', padx=20, pady=15)
            panel.pack(side='left', expand=True, fill='both', padx=(0, 10))
            tk.Label(panel, text=title, bg='white', fg='#6c7483', font=('Segoe UI', 10)).pack(anchor='w')
            value = tk.Label(panel, bg='white', fg=color, font=('Segoe UI', 22, 'bold'))
            value.pack(anchor='w', pady=(8, 0))
            self.stats.append(value)
        tabs = ttk.Notebook(outer)
        tabs.pack(fill='both', expand=True)
        activity = ttk.Frame(tabs, padding=15)
        cards = ttk.Frame(tabs, padding=15)
        tabs.add(activity, text='  Transactions  ')
        tabs.add(cards, text='  My cards  ')
        toolbar = ttk.Frame(activity)
        toolbar.pack(fill='x', pady=(0, 12))
        self.query = tk.StringVar()
        ttk.Label(toolbar, text='Search:').pack(side='left', padx=(0, 8))
        ttk.Entry(toolbar, textvariable=self.query, width=24).pack(side='left')
        self.kind = tk.StringVar(value='All')
        chooser = ttk.Combobox(toolbar, textvariable=self.kind, values=('All', 'Income', 'Expenses'), state='readonly', width=11)
        chooser.pack(side='left', padx=10)
        self.query.trace_add('write', lambda *args: self.refresh_transactions())
        chooser.bind('<<ComboboxSelected>>', lambda e: self.refresh_transactions())
        ttk.Button(toolbar, text='Export CSV', command=self.export).pack(side='right')
        self.transactions = self.table(activity, ('Date', 'Description', 'Category', 'Amount'), (110, 340, 160, 145))
        self.transactions.tag_configure('income', foreground='#21775c')
        self.transactions.tag_configure('expense', foreground='#a54848')
        self.empty_text = ttk.Label(activity, text='')
        self.empty_text.pack(anchor='w', pady=7)
        card_tools = ttk.Frame(cards)
        card_tools.pack(fill='x', pady=(0, 12))
        ttk.Label(card_tools, text='Store nicknames and last four digits only.').pack(side='left')
        ttk.Button(card_tools, text='Remove selected', command=self.remove_card).pack(side='right', padx=(8, 0))
        ttk.Button(card_tools, text='+ Add card', command=self.card_form).pack(side='right')
        self.cards = self.table(cards, ('Nickname', 'Network', 'Last four digits'), (400, 180, 180))
        ttk.Label(outer, text='Saved automatically on this device  •  INR  •  Personal ledger', foreground='#778091').pack(anchor='w', pady=(15, 0))
        self.bind('<Control-n>', lambda e: self.transaction_form(False))
        self.protocol('WM_DELETE_WINDOW', self.close)
        self.refresh()

    def table(self, parent, columns, widths):
        frame = ttk.Frame(parent)
        frame.pack(fill='both', expand=True)
        tree = ttk.Treeview(frame, columns=columns, show='headings', selectmode='browse')
        for column, width in zip(columns, widths):
            tree.heading(column, text=column)
            tree.column(column, width=width, minwidth=90, anchor='e' if column == 'Amount' else 'w')
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        tree.pack(side='left', fill='both', expand=True)
        return tree

    def refresh_transactions(self):
        self.transactions.delete(*self.transactions.get_children())
        rows = self.store.transactions(self.query.get().strip(), self.kind.get())
        for row in rows:
            incoming = row['amount'] > 0
            self.transactions.insert('', 'end', iid=str(row['id']), values=(row['day'], row['title'], row['category'],
                ('+' if incoming else '−') + money(abs(row['amount']))), tags=('income' if incoming else 'expense',))
        self.empty_text.configure(text=f'{len(rows)} transaction(s)' if rows else 'No transactions found. Add an income entry to get started.')

    def refresh(self):
        income, expenses, _ = self.store.monthly()
        for label, value in zip(self.stats, (self.store.balance, income, expenses)):
            label.configure(text=money(value))
        self.refresh_transactions()
        self.cards.delete(*self.cards.get_children())
        for card in self.store.cards():
            self.cards.insert('', 'end', iid=str(card['id']), values=(card['name'], card['network'], '•••• ' + card['last4']))

    def form(self, title, fields, submit):
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.transient(self)
        dialog.resizable(False, False)
        dialog.grab_set()
        frame = ttk.Frame(dialog, padding=24)
        frame.pack(fill='both', expand=True)
        variables = []
        first = None
        for label, options in fields:
            ttk.Label(frame, text=label).pack(anchor='w', pady=(8, 5))
            value = tk.StringVar(value=options[0] if options else '')
            widget = ttk.Combobox(frame, textvariable=value, values=options, state='readonly', width=34) if options else ttk.Entry(frame, textvariable=value, width=37)
            widget.pack(fill='x', ipady=5)
            first = first or widget
            variables.append(value)
        error = ttk.Label(frame, text='', foreground='#a54848', wraplength=340)
        error.pack(anchor='w', pady=12)
        def save(event=None):
            try:
                submit([v.get().strip() for v in variables])
            except (ValueError, OSError) as exc:
                error.configure(text=str(exc))
                return
            dialog.destroy()
            self.refresh()
        actions = ttk.Frame(frame)
        actions.pack(fill='x')
        ttk.Button(actions, text='Save', command=save).pack(side='right')
        ttk.Button(actions, text='Cancel', command=dialog.destroy).pack(side='right', padx=8)
        dialog.bind('<Return>', save)
        dialog.bind('<Escape>', lambda e: dialog.destroy())
        first.focus_set()
        return dialog

    def transaction_form(self, incoming):
        fields = [('Description', None), ('Amount (₹)', None)]
        if not incoming:
            fields.append(('Category', CATEGORIES))
        def save(values):
            self.store.add_transaction(values[0], parse_amount(values[1]) * (1 if incoming else -1), 'Income' if incoming else values[2])
        return self.form('Add income' if incoming else 'Add expense', fields, save)

    def card_form(self):
        return self.form('Add card reference', [('Nickname', None), ('Last four digits', None), ('Network', ('VISA', 'Mastercard', 'RuPay'))],
                         lambda v: self.store.add_card(v[0], v[1], v[2], '#3457b1'))

    def remove_card(self):
        selected = self.cards.selection()
        if not selected:
            messagebox.showinfo('Select a card', 'Select a card to remove.', parent=self)
            return
        if messagebox.askyesno('Remove card', 'Remove this card reference?', parent=self):
            self.store.remove('cards', int(selected[0]))
            self.refresh()

    def export(self):
        path = filedialog.asksaveasfilename(parent=self, defaultextension='.csv', initialfile='wallet-transactions.csv', filetypes=[('CSV file', '*.csv')])
        if path:
            try:
                self.store.export_csv(path)
            except OSError as exc:
                messagebox.showerror('Export failed', str(exc), parent=self)
            else:
                messagebox.showinfo('Export complete', 'All transactions exported.', parent=self)

    def close(self):
        self.store.close()
        self.destroy()


def main():
    parser = argparse.ArgumentParser(description='Basic wallet and expense manager')
    parser.add_argument('--data', type=Path, help='Custom database path')
    parser.add_argument('--demo', action='store_true', help='Include sample entries in a new database')
    args = parser.parse_args()
    base = Path(os.environ.get('LOCALAPPDATA', str(Path.home() / '.local' / 'share'))) / 'WalletMoneyManagerApp'
    WalletApp(WalletStore(args.data or base / 'wallet.db', demo=args.demo)).mainloop()


if __name__ == '__main__':
    main()
