# Wallet-Money-Manager-APP

## Pocket Semester — student money journal

The college-project edition adds an original cream-and-forest journal identity, student categories, a monthly budget with a daily spending allowance, category charts, and editable/deletable transaction records with balance protection.

See [SUBMISSION_GUIDE.md](SUBMISSION_GUIDE.md) for the abstract, architecture diagram, database design, algorithms, demonstration script, limitations and viva preparation. The implementation uses only Python's standard library.

A basic Python **Tkinter** desktop app for managing money, expenses and card references. It uses standard widgets, simple forms and a scrollable transaction table. No additional Python packages are required.

## Run

Install Python 3.10+ with Tkinter, then double-click **Start Wallet.bat** on Windows or run:

```powershell
py main.py
```

On macOS/Linux use `python3 main.py`. Linux may require your distribution's `python3-tk` package.

## Features

- Available balance and monthly income/expense totals in INR.
- Add income and categorized expenses with validation and overdraft protection.
- Search transaction descriptions or categories; filter income and expenses.
- Export all transactions to CSV.
- Add/remove card references using a nickname, network and last four digits.
- Automatic local SQLite storage; exact amounts stored as integer paise.
- Ctrl+N opens the expense form. Enter saves a form; Escape closes it.

The app starts with an empty wallet. For a separate demo wallet:

```powershell
py main.py --data demo.db --demo
```

`--demo` seeds a new database only. It never overwrites existing entries.

## Data

Windows stores data in `%LOCALAPPDATA%\WalletMoneyManagerApp\wallet.db`. Other platforms use `~/.local/share/WalletMoneyManagerApp/wallet.db`. This is separate from the advanced Aster Wallet app. Use `--data PATH` to choose a database.

The balance is a personal ledger; card references do not have separate account balances. This app does not connect to banks or process payments. Local data is not encrypted. Store only the last four card digits, never full numbers, PINs or CVVs. Databases and exports are excluded from Git.

## Files and tests

- `main.py`: basic Tkinter interface and launch options.
- `wallet_model.py`: storage, validation, totals and export.
- `test_wallet.py`: data-layer tests.
- `test_app.py`: integration checks using a temporary database.

```powershell
py -m unittest -v
```

UI tests briefly open a test window. They never access your personal wallet.

For the advanced animated version, see [Wallet-Money-Manager-UI](https://github.com/parthjaina2107/Wallet-Money-Manager-UI).
