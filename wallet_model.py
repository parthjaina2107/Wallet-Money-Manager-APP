"""Local wallet storage. Monetary values are integer paise, never binary floats."""
from __future__ import annotations

import csv
import sqlite3
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path

CATEGORIES = ("Shopping", "Food & drinks", "Transport", "Bills", "Entertainment", "Health", "Other")


def parse_amount(value: str) -> int:
    try:
        amount = Decimal(value.strip())
        if not amount.is_finite() or amount <= 0 or amount > Decimal("999999999"):
            raise ValueError("Enter an amount between ₹0.01 and ₹999,999,999.")
        if amount != amount.quantize(Decimal("0.01")):
            raise ValueError("Use at most two decimal places.")
        return int(amount * 100)
    except InvalidOperation as exc:
        raise ValueError("Enter a valid amount, for example 1250.50.") from exc


def money(paise: int) -> str:
    return f"₹{paise / 100:,.2f}"


class WalletStore:
    def __init__(self, path: Path | str, demo: bool = True):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.path)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys = ON")
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS cards(
                id INTEGER PRIMARY KEY, name TEXT NOT NULL, last4 TEXT NOT NULL,
                network TEXT NOT NULL, color TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS transactions(
                id INTEGER PRIMARY KEY, title TEXT NOT NULL, amount INTEGER NOT NULL,
                category TEXT NOT NULL, day TEXT NOT NULL);
        """)
        if self.setting("initialized") is None:
            with self.db:
                self.db.execute("INSERT INTO settings VALUES('initialized', '1')")
                self.db.execute("INSERT INTO settings VALUES('motion', '1')")
                self.db.execute("INSERT INTO settings VALUES('budget', '3000000')")
                if demo:
                    self._seed()

    def _seed(self):
        today = date.today()
        rows = [("Opening balance", 4200000, "Opening balance", today.replace(day=1)),
                ("Monthly salary", 8500000, "Income", today.replace(day=1)),
                ("Weekend groceries", -284000, "Shopping", today),
                ("Blue Tokai Coffee", -38000, "Food & drinks", today),
                ("EV charging", -125000, "Transport", today - timedelta(days=1)),
                ("Internet subscription", -99900, "Bills", today - timedelta(days=2)),
                ("Dinner with friends", -186000, "Food & drinks", today - timedelta(days=3)),
                ("New headphones", -649900, "Shopping", today - timedelta(days=5)),
                ("Movie night", -90000, "Entertainment", today - timedelta(days=7))]
        self.db.executemany("INSERT INTO transactions(title,amount,category,day) VALUES(?,?,?,?)",
                            [(title, amount, category, day.isoformat()) for title, amount, category, day in rows])
        self.db.executemany("INSERT INTO cards(name,last4,network,color) VALUES(?,?,?,?)", [
            ("Everyday card", "4829", "VISA", "#ED8C66"),
            ("Travel card", "9051", "Mastercard", "#B6B1D6"),
            ("Savings card", "2018", "RuPay", "#A7BCAC")])

    def setting(self, key, default=None):
        row = self.db.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return row[0] if row else default

    def set_setting(self, key, value):
        with self.db:
            self.db.execute("INSERT OR REPLACE INTO settings VALUES(?,?)", (key, str(value)))

    @property
    def balance(self):
        return self.db.execute("SELECT COALESCE(SUM(amount),0) FROM transactions").fetchone()[0]

    def transactions(self, query="", kind="All"):
        rows = self.db.execute("SELECT * FROM transactions ORDER BY day DESC, id DESC").fetchall()
        return [r for r in rows if query.casefold() in (r['title'] + ' ' + r['category']).casefold()
                and (kind == "All" or (r['amount'] > 0) == (kind == "Income"))]

    def monthly(self):
        prefix = date.today().strftime("%Y-%m")
        rows = [r for r in self.transactions() if r['day'].startswith(prefix) and r['category'] != 'Opening balance']
        income = sum(r['amount'] for r in rows if r['amount'] > 0)
        expenses = -sum(r['amount'] for r in rows if r['amount'] < 0)
        categories = {}
        for r in rows:
            if r['amount'] < 0:
                categories[r['category']] = categories.get(r['category'], 0) - r['amount']
        return income, expenses, sorted(categories.items(), key=lambda p: -p[1])

    def add_transaction(self, title, amount, category):
        if not title.strip() or len(title.strip()) > 60:
            raise ValueError("Use a description between 1 and 60 characters.")
        if type(amount) is not int or amount == 0:
            raise ValueError("Amount must be a nonzero integer in paise.")
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            if amount < 0 and -amount > self.balance:
                raise ValueError("This expense exceeds your available balance.")
            self.db.execute("INSERT INTO transactions(title,amount,category,day) VALUES(?,?,?,?)",
                            (title.strip(), amount, category, date.today().isoformat()))

    def cards(self):
        return self.db.execute("SELECT * FROM cards ORDER BY id").fetchall()

    def add_card(self, name, last4, network, color):
        if not name.strip() or len(name.strip()) > 30:
            raise ValueError("Use a card name between 1 and 30 characters.")
        if len(last4) != 4 or not last4.isascii() or not last4.isdigit():
            raise ValueError("Enter exactly the last four digits of your card.")
        if network not in ("VISA", "Mastercard", "RuPay"):
            raise ValueError("Choose a supported card network.")
        with self.db:
            self.db.execute("INSERT INTO cards(name,last4,network,color) VALUES(?,?,?,?)", (name.strip(), last4, network, color))

    def remove(self, table, item_id):
        if table != "cards":
            raise ValueError("Unsupported collection.")
        with self.db:
            self.db.execute(f"DELETE FROM {table} WHERE id=?", (item_id,))

    def export_csv(self, path):
        with open(path, "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file)
            writer.writerow(["Date", "Description", "Category", "Amount (INR)"])
            for row in self.transactions():
                # Prevent spreadsheet formula evaluation in user-entered descriptions.
                title = row['title']
                if title.lstrip().startswith(('=', '+', '-', '@')):
                    title = "'" + title
                writer.writerow([row['day'], title, row['category'], f"{Decimal(row['amount']) / 100:.2f}"])

    def close(self):
        self.db.close()
