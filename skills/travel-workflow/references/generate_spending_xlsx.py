#!/usr/bin/env python3
"""Generate a travel-planner spending spreadsheet (<dest>-spending.xlsx).

The spending tracker's money lives here, in a standalone XLSX with LIVE FORMULAS,
not in a hand-recalculated markdown table. See spending-integration.md for the
schema, the source-of-truth rules, and the mandatory recalc-validation step.

Contract (see spending-integration.md):
  * Formulas are written as STRINGS — openpyxl does not compute cached results.
    Never trust a raw read of the totals; recalc-validate (e.g. LibreOffice
    headless) before quoting any figure.
  * Regeneration keys on ID: `## Bookings` drives the identity rows; Amount and
    Trip budget are user-editable INPUTS and are preserved by ID across regen so
    a hand-entered amount is never clobbered.

Usage:
  # As a library:
  from generate_spending_xlsx import generate_spending_xlsx
  generate_spending_xlsx(bookings, budget, "tokyo-spending.xlsx")

  # As a CLI (bookings + budget supplied as a JSON file):
  python generate_spending_xlsx.py bookings.json tokyo-spending.xlsx
  # bookings.json: {"budget": 3000, "bookings": [
  #   {"id": "tyo-bk1", "item": "Tokyo flight (JAL 123)", "conf": "ABC123",
  #    "pay": "prepaid", "amount": 450}, ... ]}

  # Self-test (writes a sample file and prints where):
  python generate_spending_xlsx.py --demo
"""
from __future__ import annotations

import json
import os
import sys

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

# --- layout constants (the single source of the cell layout) ---------------
HEADERS = ["ID", "Item", "Confirmation #", "Payment status", "Amount"]
FIRST_DATA_ROW = 2
LAST_DATA_ROW = 200          # formulas span E2:E200, so appended rows are covered
SUMMARY_TOTAL = 202
SUMMARY_BUDGET = 203
SUMMARY_REMAINING = 204
SUMMARY_DUE = 205

INPUT_FILL = PatternFill("solid", fgColor="FFF2CC")    # yellow = editable input
FORMULA_FILL = PatternFill("solid", fgColor="D9D9D9")   # grey = calculated
MONEY_FMT = '"$"#,##0.00'
PAY_STATUSES = ("prepaid", "due-on-arrival", "points")


def _read_existing_inputs(path: str):
    """Return (amounts_by_id, budget) preserved from an existing file, so a
    regeneration doesn't clobber user-entered Amount/Budget inputs. Amount and
    the budget are plain input cells (not formulas), so a normal load reads them."""
    amounts: dict[str, object] = {}
    budget = None
    if not os.path.exists(path):
        return amounts, budget
    wb = load_workbook(path)
    ws = wb["Spending"] if "Spending" in wb.sheetnames else wb.active
    for row in range(FIRST_DATA_ROW, LAST_DATA_ROW + 1):
        rid = ws.cell(row, 1).value
        if rid:
            amounts[str(rid)] = ws.cell(row, 5).value
    budget = ws.cell(SUMMARY_BUDGET, 5).value
    return amounts, budget


def generate_spending_xlsx(bookings, budget=None, out_path="spending.xlsx",
                           preserve_existing_inputs=True):
    """Write the spending spreadsheet.

    bookings: iterable of dicts with keys id, item, conf, pay, amount
              (amount may be None/absent => blank => excluded from totals).
    budget:   trip budget number, or None to leave it unset.
    """
    preserved_amounts, preserved_budget = ({}, None)
    if preserve_existing_inputs:
        preserved_amounts, preserved_budget = _read_existing_inputs(out_path)
    if budget is None:
        budget = preserved_budget

    wb = Workbook()
    ws = wb.active
    ws.title = "Spending"

    # header row
    ws.append(HEADERS)
    for col in range(1, 6):
        ws.cell(1, col).font = Font(bold=True)
        ws.cell(1, col).fill = INPUT_FILL

    # payment-status dropdown
    dv = DataValidation(type="list", formula1='"%s"' % ",".join(PAY_STATUSES),
                        allow_blank=True)
    ws.add_data_validation(dv)
    dv.add("D%d:D%d" % (FIRST_DATA_ROW, LAST_DATA_ROW))

    # data rows
    row = FIRST_DATA_ROW
    for b in bookings:
        bid = str(b["id"])
        amount = b.get("amount")
        # preserve a user-edited amount when the caller didn't supply one
        if amount is None and bid in preserved_amounts:
            amount = preserved_amounts[bid]
        ws.cell(row, 1, bid)
        ws.cell(row, 2, b.get("item"))
        ws.cell(row, 3, b.get("conf"))
        ws.cell(row, 4, b.get("pay"))
        ws.cell(row, 5, amount)                 # None => blank cell => excluded
        ws.cell(row, 5).number_format = MONEY_FMT
        for col in range(1, 6):
            ws.cell(row, col).fill = INPUT_FILL
        row += 1

    # summary block — formulas are written as STRINGS (recalc-validate before trusting)
    ws.cell(SUMMARY_TOTAL, 2, "Total spent")
    ws.cell(SUMMARY_TOTAL, 5, "=SUM(E%d:E%d)" % (FIRST_DATA_ROW, LAST_DATA_ROW))
    ws.cell(SUMMARY_BUDGET, 2, "Trip budget")
    ws.cell(SUMMARY_BUDGET, 5, budget)
    ws.cell(SUMMARY_REMAINING, 2, "Remaining")
    ws.cell(SUMMARY_REMAINING, 5, "=E%d-E%d" % (SUMMARY_BUDGET, SUMMARY_TOTAL))
    ws.cell(SUMMARY_DUE, 2, "Still due in person")
    ws.cell(SUMMARY_DUE, 5, '=SUMIF(D%d:D%d,"due-on-arrival",E%d:E%d)'
            % (FIRST_DATA_ROW, LAST_DATA_ROW, FIRST_DATA_ROW, LAST_DATA_ROW))

    for r in (SUMMARY_TOTAL, SUMMARY_REMAINING, SUMMARY_DUE):
        c = ws.cell(r, 5)
        c.fill = FORMULA_FILL
        c.font = Font(bold=True)
        c.number_format = MONEY_FMT
        ws.cell(r, 2).font = Font(bold=True)
    ws.cell(SUMMARY_BUDGET, 5).fill = INPUT_FILL          # budget is an input
    ws.cell(SUMMARY_BUDGET, 5).number_format = MONEY_FMT

    # legend
    ws.cell(SUMMARY_DUE + 2, 2,
            "Yellow = editable input. Grey = calculated — don't type over it.")

    # column widths for readability
    for col, width in zip("ABCDE", (12, 34, 16, 16, 14)):
        ws.column_dimensions[col].width = width

    wb.save(out_path)
    return out_path


def _demo():
    bookings = [
        {"id": "tyo-bk1", "item": "Tokyo flight (JAL 123)", "conf": "ABC123",
         "pay": "prepaid", "amount": 450},
        {"id": "tyo-bk2", "item": "Hotel Shinjuku (3 nights)", "conf": "XYZ789",
         "pay": "due-on-arrival", "amount": 600},
        {"id": "tyo-bk3", "item": "Robot Restaurant (points)", "conf": "PTS001",
         "pay": "points", "amount": None},
        {"id": "tyo-bk4", "item": "Day tour (price TBC)", "conf": "TBC002",
         "pay": "due-on-arrival", "amount": None},   # unpriced => blank => excluded
    ]
    out = generate_spending_xlsx(bookings, budget=3000, out_path="demo-spending.xlsx")
    print("wrote %s" % os.path.abspath(out))
    print("Expected after recalc: Total 1050, Remaining 1950, Still due 600,"
          " 1 unpriced booking.")


def main(argv):
    if len(argv) == 2 and argv[1] == "--demo":
        _demo()
        return 0
    if len(argv) != 3:
        print(__doc__)
        return 2
    with open(argv[1], encoding="utf-8") as fh:
        data = json.load(fh)
    out = generate_spending_xlsx(data.get("bookings", []), data.get("budget"),
                                 argv[2])
    print("wrote %s" % os.path.abspath(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
