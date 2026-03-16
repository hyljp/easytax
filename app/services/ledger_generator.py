import csv
import os
from decimal import Decimal


def _clean_amount(amount):
    if not amount:
        return Decimal("0")
    return Decimal(str(amount).replace("¥", "").replace(",", ""))


def create_general_ledger(input_csv, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    ledger = {}
    date_part = None

    with open(input_csv, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if date_part is None:
                date_part = row["日付"][:6].replace("-", "")

            debit_acct = row["借方科目"]
            credit_acct = row["貸方科目"]

            if debit_acct:
                ledger.setdefault(debit_acct, []).append({
                    "日付": row["日付"],
                    "借方": row["金額"],
                    "貸方": "",
                    "伝票番号": row["伝票番号"],
                    "概要": row["概要"],
                })

            if credit_acct:
                ledger.setdefault(credit_acct, []).append({
                    "日付": row["日付"],
                    "借方": "",
                    "貸方": row["金額"],
                    "伝票番号": row["伝票番号"],
                    "概要": row["概要"],
                })

    output_files = []
    messages = []
    for account, entries in ledger.items():
        if not account:
            continue
        out_name = f"{account}_{date_part}.csv"
        out_path = os.path.join(output_dir, out_name)
        with open(out_path, mode="w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["日付", "借方", "貸方", "伝票番号", "概要"])
            writer.writeheader()
            writer.writerows(entries)
        output_files.append(out_path)
        messages.append(f"作成: {out_name}")

    return output_files, date_part, messages


def generate_trial_balance(ledger_files, date_part, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    trial_balance = {}
    for ledger_file in ledger_files:
        # Use rsplit to handle account names containing underscores
        # Filename format: {account}_{YYYYMM}.csv
        basename = os.path.basename(ledger_file)
        name_without_ext = os.path.splitext(basename)[0]
        account_name = name_without_ext.rsplit("_", 1)[0]
        with open(ledger_file, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if account_name not in trial_balance:
                    trial_balance[account_name] = {"借方": Decimal("0"), "貸方": Decimal("0")}
                if row["借方"]:
                    trial_balance[account_name]["借方"] += _clean_amount(row["借方"])
                if row["貸方"]:
                    trial_balance[account_name]["貸方"] += _clean_amount(row["貸方"])

    out_path = os.path.join(output_dir, f"試算表_{date_part}.csv")
    total_debit = Decimal("0")
    total_credit = Decimal("0")

    with open(out_path, mode="w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["科目", "借方", "貸方"])
        for account, amounts in trial_balance.items():
            d = amounts["借方"] if amounts["借方"] != 0 else ""
            c = amounts["貸方"] if amounts["貸方"] != 0 else ""
            writer.writerow([account, d, c])
            total_debit += amounts["借方"]
            total_credit += amounts["貸方"]
        writer.writerow(["合計", total_debit or "", total_credit or ""])

    return out_path


def generate_yearly_trial_balance(monthly_tb_files, year, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    yearly = {}
    for tb_file in monthly_tb_files:
        with open(tb_file, mode="r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            next(reader)  # skip header
            for row in reader:
                if len(row) < 3 or row[0] == "合計":
                    continue
                account = row[0]
                if account not in yearly:
                    yearly[account] = {"借方": Decimal("0"), "貸方": Decimal("0")}
                if row[1]:
                    yearly[account]["借方"] += _clean_amount(row[1])
                if row[2]:
                    yearly[account]["貸方"] += _clean_amount(row[2])

    out_path = os.path.join(output_dir, f"試算表_{year}_年度.csv")
    total_debit = Decimal("0")
    total_credit = Decimal("0")

    with open(out_path, mode="w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["科目", "借方", "貸方"])
        for account, amounts in yearly.items():
            d = amounts["借方"] if amounts["借方"] != 0 else ""
            c = amounts["貸方"] if amounts["貸方"] != 0 else ""
            writer.writerow([account, d, c])
            total_debit += amounts["借方"]
            total_credit += amounts["貸方"]
        writer.writerow(["合計", total_debit or "", total_credit or ""])

    return out_path
