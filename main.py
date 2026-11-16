"""Aster Wallet: a standalone Tkinter GUI with temporary demo values."""
import tkinter as tk
from datetime import date
from tkinter import ttk, messagebox
from decimal import Decimal, InvalidOperation

CATEGORIES = ('Food & drinks', 'Transport', 'Books & stationery', 'College fees',
              'Subscriptions', 'Shopping', 'Bills', 'Entertainment', 'Health', 'Other')


def money(value):
    return f'₹{value:,.2f}'


def parse_amount(text):
    try:
        value = Decimal(text)
        if not value.is_finite() or not Decimal('0') < value <= Decimal('999999999'):
            raise ValueError('Enter an amount between 0.01 and 999,999,999.')
        if value != value.quantize(Decimal('0.01')):
            raise ValueError('Use at most two decimal places.')
        return value
    except InvalidOperation as exc:
        raise ValueError('Enter a valid amount, for example 150.50.') from exc


class WalletApp(tk.Tk):
    def __init__(self):
        super().__init__()
        today = date.today().isoformat()
        self.entries = [
            {'id': 1, 'title': 'Monthly allowance', 'amount': Decimal('5000'), 'category': 'Income', 'day': today},
            {'id': 2, 'title': 'Lunch with friends', 'amount': Decimal('-150'), 'category': 'Food & drinks', 'day': today},
            {'id': 3, 'title': 'Lab manual', 'amount': Decimal('-400'), 'category': 'Books & stationery', 'day': today},
            {'id': 4, 'title': 'Bus travel', 'amount': Decimal('-100'), 'category': 'Transport', 'day': today},
        ]
        self.card_items = [{'id': 1, 'name': 'Campus card', 'network': 'VISA', 'last4': '1234'}]
        self.next_entry_id = 5
        self.next_card_id = 2
        self.budget = Decimal('3000')
        self.title('Aster Wallet | Tkinter GUI Demo')
        self.geometry('1160x820')
        self.minsize(1050, 720)
        self.configure(bg='#f5f2e9')
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TFrame', background='#f5f2e9')
        style.configure('TLabel', background='#f5f2e9', foreground='#263f37', font=('Segoe UI', 11))
        style.configure('TNotebook', background='#f5f2e9', borderwidth=0)
        style.configure('TNotebook.Tab', padding=(18, 10), font=('Segoe UI', 10, 'bold'))
        style.map('TNotebook.Tab', background=[('selected', '#214d40')], foreground=[('selected', 'white')])
        style.configure('Accent.TButton', background='#214d40', foreground='white')
        style.map('Accent.TButton', background=[('active', '#316552')])
        style.configure('TButton', font=('Segoe UI', 10), padding=9)
        style.configure('Treeview', rowheight=33, font=('Segoe UI', 10), background='white', fieldbackground='white')
        style.configure('Treeview.Heading', font=('Segoe UI', 10, 'bold'), padding=8)
        outer = ttk.Frame(self, padding=24)
        outer.pack(fill='both', expand=True)
        header = ttk.Frame(outer)
        header.pack(fill='x')
        ttk.Label(header, text='ASTER WALLET', font=('Segoe UI', 25, 'bold')).pack(side='left')
        ttk.Button(header, text='+ Income', command=lambda: self.transaction_form(True)).pack(side='right', padx=(8, 0))
        ttk.Button(header, text='+ Expense', command=lambda: self.transaction_form(False)).pack(side='right')
        ttk.Label(outer, text='Explore your wallet interface with sample values.', foreground='#67786e').pack(anchor='w', pady=(6, 0))
        summary = ttk.Frame(outer, padding=(0, 20))
        summary.pack(fill='x')
        self.stats = []
        for title, color in [('01 / AVAILABLE TO YOU', '#214d40'), ('02 / MONEY IN THIS MONTH', '#21775c'), ('03 / MONEY OUT THIS MONTH', '#b85151')]:
            panel = tk.Frame(summary, bg='white', padx=20, pady=15)
            panel.pack(side='left', expand=True, fill='both', padx=(0, 10))
            tk.Label(panel, text=title, bg='white', fg='#6c7483', font=('Segoe UI', 10)).pack(anchor='w')
            value = tk.Label(panel, bg='white', fg=color, font=('Segoe UI', 22, 'bold'))
            value.pack(anchor='w', pady=(8, 0))
            self.stats.append(value)
        pace = tk.Frame(outer, bg='#214d40', padx=20, pady=14)
        pace.pack(fill='x', pady=(0, 18))
        self.pace_text = tk.Label(pace, bg='#214d40', fg='#fff9e8', font=('Segoe UI', 13, 'bold'), anchor='w')
        self.pace_text.pack(side='left')
        ttk.Button(pace, text='Set monthly budget', command=self.budget_form).pack(side='right')
        ttk.Label(outer, text='Interactive GUI demo  •  Changes reset when you close the window', foreground='#67786e').pack(side='bottom', anchor='w', pady=(12, 0))
        tabs = ttk.Notebook(outer)
        self.tabs = tabs
        tabs.pack(fill='both', expand=True)
        activity = ttk.Frame(tabs, padding=15)
        cards = ttk.Frame(tabs, padding=15)
        tabs.add(activity, text='  Transactions  ')
        tabs.add(cards, text='  My cards  ')
        insights = ttk.Frame(tabs, padding=18)
        tabs.add(insights, text='  Spending story  ')
        ttk.Label(insights, text='Where did this month go?', font=('Segoe UI', 19, 'bold')).pack(anchor='w')
        ttk.Label(insights, text='Sample expenses grouped by category — updates as you try the forms.', foreground='#67786e').pack(anchor='w', pady=(5, 12))
        chart_frame = ttk.Frame(insights)
        chart_frame.pack(fill='both', expand=True)
        self.chart = tk.Canvas(chart_frame, bg='#f5f2e9', highlightthickness=0)
        chart_scroll = ttk.Scrollbar(chart_frame, orient='vertical', command=self.chart.yview)
        self.chart.configure(yscrollcommand=chart_scroll.set)
        chart_scroll.pack(side='right', fill='y')
        self.chart.pack(side='left', fill='both', expand=True)
        self.chart.bind('<Configure>', lambda e: self.draw_chart())
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
        self.empty_text = ttk.Label(activity, text='')
        self.empty_text.pack(side='bottom', anchor='w', pady=7)
        edits = ttk.Frame(activity)
        edits.pack(side='bottom', fill='x')
        ttk.Button(edits, text='Edit selected', command=self.edit_transaction).pack(side='left')
        ttk.Button(edits, text='Delete selected', command=self.delete_transaction).pack(side='left', padx=8)
        self.transactions = self.table(activity, ('Date', 'Description', 'Category', 'Amount'), (110, 340, 160, 145))
        self.transactions.tag_configure('income', foreground='#21775c')
        self.transactions.tag_configure('expense', foreground='#a54848')
        self.transactions.bind('<Double-1>', lambda e: self.edit_transaction())
        card_tools = ttk.Frame(cards)
        card_tools.pack(fill='x', pady=(0, 12))
        ttk.Label(card_tools, text='Store nicknames and last four digits only.').pack(side='left')
        ttk.Button(card_tools, text='Remove selected', command=self.remove_card).pack(side='right', padx=(8, 0))
        ttk.Button(card_tools, text='+ Add card', command=self.card_form).pack(side='right')
        self.cards = self.table(cards, ('Nickname', 'Network', 'Last four digits'), (400, 180, 180))
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
        query = self.query.get().strip().casefold()
        kind = self.kind.get()
        rows = [row for row in reversed(self.entries)
                if query in (row['title'] + ' ' + row['category']).casefold()
                and (kind == 'All' or (row['amount'] > 0) == (kind == 'Income'))]
        for row in rows:
            incoming = row['amount'] > 0
            self.transactions.insert('', 'end', iid=str(row['id']), values=(row['day'], row['title'], row['category'],
                ('+' if incoming else '−') + money(abs(row['amount']))), tags=('income' if incoming else 'expense',))
        self.empty_text.configure(text=f'{len(rows)} transaction(s)' if rows else 'No transactions found. Add an income entry to get started.')

    def refresh(self):
        income, expenses, _ = self.monthly_values()
        for label, value in zip(self.stats, (self.balance, income, expenses)):
            label.configure(text=money(value))
        self.refresh_transactions()
        self.pace_text.configure(text=f'Demo monthly budget: {money(self.budget)}   ·   Spent: {money(expenses)}')
        self.draw_chart()
        self.cards.delete(*self.cards.get_children())
        for card in self.card_items:
            self.cards.insert('', 'end', iid=str(card['id']), values=(card['name'], card['network'], '•••• ' + card['last4']))

    def draw_chart(self):
        self.chart.delete('all')
        _, total, categories = self.monthly_values()
        width = max(500, self.chart.winfo_width())
        if not categories:
            self.chart.create_text(18, 40, anchor='w', text='Your first expense will start the story.', fill='#67786e', font=('Segoe UI', 14))
            self.chart.configure(scrollregion=(0, 0, width, 80))
            return
        for i, (name, value) in enumerate(categories):
            y = 22 + i * 48
            self.chart.create_text(8, y, anchor='w', text=name, fill='#263f37', font=('Segoe UI', 10, 'bold'))
            self.chart.create_text(width-20, y, anchor='e', text=f'{money(value)}  ·  {value/total:.0%}', fill='#67786e', font=('Segoe UI', 10))
            self.chart.create_line(8, y+18, width-20, y+18, fill='#e3dfd1', width=7)
            self.chart.create_line(8, y+18, 8+(width-28)*float(value/total), y+18, fill=('#32735c','#b78b44','#718a9b')[i%3], width=7)
        self.chart.configure(scrollregion=(0, 0, width, len(categories)*48+20))

    def budget_form(self):
        return self.form('Monthly spending budget', [('Budget in ₹', None)],
                         lambda v: setattr(self, 'budget', parse_amount(v[0])))

    def selected_transaction(self):
        selected = self.transactions.selection()
        if not selected:
            messagebox.showinfo('Choose an entry', 'Select a transaction first.', parent=self)
            return None
        return next((r for r in self.entries if r['id'] == int(selected[0])), None)

    def edit_transaction(self):
        row = self.selected_transaction()
        if row is None:
            return
        fields = [('Description', None), ('Amount (₹)', None), ('Date (YYYY-MM-DD)', None)]
        if row['amount'] < 0:
            fields.append(('Category', CATEGORIES))
        def save(v):
            title = self.checked_title(v[0])
            amount = parse_amount(v[1]) * (1 if row['amount'] > 0 else -1)
            day = date.fromisoformat(v[2])
            if day > date.today():
                raise ValueError('Choose today or an earlier date.')
            if self.balance - row['amount'] + amount < 0:
                raise ValueError('This change exceeds the displayed balance.')
            row.update(title=title, amount=amount, day=day.isoformat(),
                       category=row['category'] if amount > 0 else v[3])
        initial = [row['title'], f"{abs(row['amount']):.2f}", row['day']]
        if row['amount'] < 0:
            initial.append(row['category'])
        return self.form('Edit journal entry', fields, save, initial)

    def delete_transaction(self):
        row = self.selected_transaction()
        if row is None:
            return
        if messagebox.askyesno('Delete journal entry', f"Delete '{row['title']}'? This cannot be undone.", parent=self):
            try:
                if self.balance - row['amount'] < 0:
                    raise ValueError('Removing this income would make the displayed balance negative.')
                self.entries.remove(row)
            except ValueError as exc:
                messagebox.showerror('Cannot delete entry', str(exc), parent=self)
            self.refresh()

    def form(self, title, fields, submit, initial=None):
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.transient(self)
        dialog.resizable(False, False)
        dialog.grab_set()
        frame = ttk.Frame(dialog, padding=24)
        frame.pack(fill='both', expand=True)
        variables = []
        first = None
        for index, (label, options) in enumerate(fields):
            ttk.Label(frame, text=label).pack(anchor='w', pady=(8, 5))
            value = tk.StringVar(value=initial[index] if initial else (options[0] if options else ''))
            widget = ttk.Combobox(frame, textvariable=value, values=options, state='readonly', width=34) if options else ttk.Entry(frame, textvariable=value, width=37)
            widget.pack(fill='x', ipady=5)
            first = first or widget
            variables.append(value)
        error = ttk.Label(frame, text='', foreground='#a54848', wraplength=340)
        error.pack(anchor='w', pady=12)
        def save(event=None):
            try:
                submit([v.get().strip() for v in variables])
            except ValueError as exc:
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
            title = self.checked_title(values[0])
            amount = parse_amount(values[1]) * (1 if incoming else -1)
            if self.balance + amount < 0:
                raise ValueError('This expense exceeds the displayed balance.')
            self.entries.append({'id': self.next_entry_id, 'title': title, 'amount': amount,
                                 'category': 'Income' if incoming else values[2],
                                 'day': date.today().isoformat()})
            self.next_entry_id += 1
        return self.form('Add income' if incoming else 'Add expense', fields, save)

    def card_form(self):
        return self.form('Add card reference', [('Nickname', None), ('Last four digits', None), ('Network', ('VISA', 'Mastercard', 'RuPay'))],
                         self.add_card_preview)

    def remove_card(self):
        selected = self.cards.selection()
        if not selected:
            messagebox.showinfo('Select a card', 'Select a card to remove.', parent=self)
            return
        if messagebox.askyesno('Remove card', 'Remove this card reference?', parent=self):
            self.card_items = [c for c in self.card_items if c['id'] != int(selected[0])]
            self.refresh()

    @property
    def balance(self):
        return sum((row['amount'] for row in self.entries), Decimal('0'))

    def monthly_values(self):
        rows = [r for r in self.entries if r['day'].startswith(date.today().strftime('%Y-%m'))]
        income = sum((r['amount'] for r in rows if r['amount'] > 0), Decimal('0'))
        categories = {}
        for row in rows:
            if row['amount'] < 0:
                categories[row['category']] = categories.get(row['category'], Decimal('0')) - row['amount']
        return income, sum(categories.values(), Decimal('0')), sorted(categories.items(), key=lambda item: -item[1])

    @staticmethod
    def checked_title(text):
        if not text.strip() or len(text.strip()) > 60:
            raise ValueError('Use a description between 1 and 60 characters.')
        return text.strip()

    def add_card_preview(self, values):
        name = self.checked_title(values[0])
        if len(values[1]) != 4 or not values[1].isascii() or not values[1].isdigit():
            raise ValueError('Enter exactly four digits.')
        self.card_items.append({'id': self.next_card_id, 'name': name,
                                'last4': values[1], 'network': values[2]})
        self.next_card_id += 1

    def close(self):
        self.destroy()


if __name__ == '__main__':
    WalletApp().mainloop()
