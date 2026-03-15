import csv
import os
from datetime import datetime


class DuplicateVoucherError(Exception):
    pass


class DuplicateEntryError(Exception):
    pass


def write_to_journal(data_dict, headers, fields, output_dir="./output"):
    """
    Write a journal entry to CSV.

    data_dict: {"date": ..., "price": ..., "comment": ..., "account_item": ..., "payment_method": ..., "voucher_number": ...}
    headers: list of column header names from config (e.g. ["日付", "金額", ...])
    fields: list of field keys from config (e.g. ["date", "price", ...])
    """
    os.makedirs(output_dir, exist_ok=True)

    date = data_dict["date"]
    year_month = date[:6]
    filename = f"仕訳帳_{year_month}.csv"
    filepath = os.path.join(output_dir, filename)

    if not os.path.exists(filepath):
        with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
            csv.writer(f).writerow(headers)

    rows = []
    with open(filepath, "r", newline="", encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))

    # Build new row from fields mapping
    new_row = [str(data_dict.get(field, "")) for field in fields]

    # Duplicate checks using field indices
    voucher_idx = fields.index("voucher_number") if "voucher_number" in fields else None
    date_idx = fields.index("date") if "date" in fields else None
    price_idx = fields.index("price") if "price" in fields else None

    if voucher_idx is not None:
        voucher = new_row[voucher_idx]
        for row in rows[1:]:
            if len(row) > voucher_idx and row[voucher_idx] == voucher:
                raise DuplicateVoucherError(f"伝票番号 {voucher} は既に存在します。")

    if date_idx is not None and price_idx is not None:
        for row in rows[1:]:
            if len(row) > max(date_idx, price_idx) and row[date_idx] == new_row[date_idx] and row[price_idx] == new_row[price_idx]:
                raise DuplicateEntryError(f"同じ日付({new_row[date_idx]})と金額({new_row[price_idx]})のデータが既に存在します。")

    rows.append(new_row)

    data_rows = rows[1:]
    if date_idx is not None:
        data_rows.sort(key=lambda x: datetime.strptime(x[date_idx], "%Y%m%d") if len(x) > date_idx and x[date_idx] else datetime.min)

    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(data_rows)

    return filepath, new_row
