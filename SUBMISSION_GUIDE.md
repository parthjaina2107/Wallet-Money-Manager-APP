# Aster Wallet: Tkinter GUI project

## Team members

Parth Jaina and Ronit Bhomia

## Project abstract

Aster Wallet demonstrates a student wallet interface using Python and Tkinter. It displays sample balances and transactions, provides interactive entry forms, shows masked card references and draws category spending bars. All changes exist only while the window is open. Reopening the application restores the fictional samples.

## Scope and objectives

This project focuses on GUI design, layout, event handling, navigation and form validation. The application consists of one Python file and uses only standard-library modules. Its entry forms update temporary Python lists inside the window class so each interaction can be demonstrated.

## Interface components

| Component | Tkinter widgets | Purpose |
|---|---|---|
| Dashboard | Frame, Label | Display sample balance and monthly totals |
| Navigation | ttk.Notebook | Switch between three views |
| Transactions and cards | ttk.Treeview, Scrollbar | Show rows and select items |
| Search and forms | Entry, Combobox, StringVar | Collect text and filter the displayed entries |
| Dialogs | Toplevel, Button, messagebox | Add, edit, confirm or cancel changes |
| Spending story | Canvas, Scrollbar | Draw category labels and proportional bars |

## How interaction works

Tkinter's main loop listens for events. A button invokes its callback, which reads the form values and displays validation feedback when necessary. Valid input changes temporary sample values, then refreshes the labels, tables and chart. Decimal values keep the displayed currency calculations exact.

## Demonstration

1. Run `py main.py` and explain the sample balance of ₹4,350.
2. Search for the lab manual and switch between income and expenses.
3. Add a sample expense and show the updated labels and chart.
4. Edit the lab manual from ₹400 to ₹350.
5. Enter invalid text or an expense above the displayed balance to show feedback.
6. Add a fictional card reference using the last four digits only, then remove it.
7. Change the demo monthly budget.
8. Close and reopen the application to show that sample values reset.

## Verification

Run `py -m unittest -v`. The tests open real Tkinter windows and exercise the visible controls, navigation, validation and reset behavior.

## Viva preparation

- `Tk` creates the main window and `mainloop` dispatches GUI events.
- `ttk` provides themed controls such as Notebook, Treeview and Combobox.
- `pack` and padding arrange widgets and control how they expand.
- `StringVar` links input values to callbacks used by search and forms.
- `Toplevel` creates forms that belong to the main window.
- `Canvas` draws the category chart using text and lines.
- Sample values stay in Python lists attached to the window object.

## Submission notes

Include the source, screenshots and actual verification output. Add your course and roll numbers as required. Explain reused code and AI assistance according to your college's rules. Present this as a GUI demonstration, with temporary sample interactions.
