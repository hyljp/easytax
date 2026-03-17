import csv
import os
from decimal import Decimal


def _clean_amount(value):
    if not value:
        return Decimal("0")
    return Decimal(str(value).replace("¥", "").replace(",", ""))


def generate_income_statement(tb_csv, config_data, year, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    revenue_accounts = config_data.get("収益", [])
    expense_accounts = config_data.get("費用", [])

    revenues = {}
    expenses = {}

    with open(tb_csv, mode="r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        for row in reader:
            if len(row) < 3 or row[0] == "合計":
                continue
            account = row[0]
            debit = _clean_amount(row[1])
            credit = _clean_amount(row[2])

            if account in revenue_accounts:
                revenues[account] = credit - debit
            elif account in expense_accounts:
                expenses[account] = debit - credit

    total_revenue = sum(revenues.values(), Decimal("0"))
    total_expense = sum(expenses.values(), Decimal("0"))
    net_income = total_revenue - total_expense

    out_path = os.path.join(output_dir, f"損益計算書_{year}.csv")
    with open(out_path, mode="w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["損益計算書", f"{year}年度"])
        writer.writerow([])
        writer.writerow(["【収益の部】"])
        for account, amount in revenues.items():
            if amount != 0:
                writer.writerow([account, amount])
        writer.writerow(["収益合計", total_revenue])
        writer.writerow([])
        writer.writerow(["【費用の部】"])
        for account, amount in expenses.items():
            if amount != 0:
                writer.writerow([account, amount])
        writer.writerow(["費用合計", total_expense])
        writer.writerow([])
        writer.writerow(["当期純利益", net_income])

    return out_path


def generate_balance_sheet(tb_csv, config_data, year, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    asset_accounts = config_data.get("資産", [])
    liability_accounts = config_data.get("負債", [])
    equity_accounts = config_data.get("純資産", [])
    revenue_accounts = config_data.get("収益", [])
    expense_accounts = config_data.get("費用", [])

    assets = {}
    liabilities = {}
    equity = {}
    total_revenue = Decimal("0")
    total_expense = Decimal("0")

    with open(tb_csv, mode="r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        for row in reader:
            if len(row) < 3 or row[0] == "合計":
                continue
            account = row[0]
            debit = _clean_amount(row[1])
            credit = _clean_amount(row[2])

            if account in asset_accounts:
                assets[account] = debit - credit
            elif account in liability_accounts:
                liabilities[account] = credit - debit
            elif account in equity_accounts:
                equity[account] = credit - debit
            elif account in revenue_accounts:
                total_revenue += credit - debit
            elif account in expense_accounts:
                total_expense += debit - credit

    net_income = total_revenue - total_expense

    total_assets = sum(assets.values(), Decimal("0"))
    total_liabilities = sum(liabilities.values(), Decimal("0"))
    total_equity = sum(equity.values(), Decimal("0")) + net_income
    total_liab_equity = total_liabilities + total_equity

    out_path = os.path.join(output_dir, f"貸借対照表_{year}.csv")
    with open(out_path, mode="w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["貸借対照表", f"{year}年度"])
        writer.writerow([])
        writer.writerow(["【資産の部】"])
        for account, amount in assets.items():
            if amount != 0:
                writer.writerow([account, amount])
        writer.writerow(["資産合計", total_assets])
        writer.writerow([])
        writer.writerow(["【負債の部】"])
        for account, amount in liabilities.items():
            if amount != 0:
                writer.writerow([account, amount])
        writer.writerow(["負債合計", total_liabilities])
        writer.writerow([])
        writer.writerow(["【純資産の部】"])
        for account, amount in equity.items():
            if amount != 0:
                writer.writerow([account, amount])
        if net_income != 0:
            writer.writerow(["当期純利益", net_income])
        writer.writerow(["純資産合計", total_equity])
        writer.writerow([])
        writer.writerow(["負債・純資産合計", total_liab_equity])

    return out_path
