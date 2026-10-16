#!/usr/bin/env python3
"""CSV Data Cleaner: tidies a messy CSV and reports every problem it finds.

Usage:
    python clean.py sample_data/messy_contacts.csv
    python clean.py input.csv -o cleaned.csv -e errors.csv

Columns are detected by header name: anything containing "phone", "email",
"date" or "name" gets the matching cleaning rule. Other columns are only trimmed.
"""
import argparse
import csv
import re
import sys
from datetime import datetime

DATE_FORMATS = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y", "%d %b %Y", "%d %B %Y", "%b %d, %Y"]
EMAIL_RE = re.compile(r"^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$")
KE_PHONE_RE = re.compile(r"^\+254[17]\d{8}$")


def clean_text(value):
    return re.sub(r"\s+", " ", value or "").strip()


def clean_name(value):
    value = clean_text(value)
    return value.title() if value else value


def clean_email(value):
    value = clean_text(value).lower().replace(" ", "")
    if not value:
        return value, None
    return (value, None) if EMAIL_RE.match(value) else (value, "invalid email")


def clean_phone(value):
    raw = clean_text(value)
    if not raw:
        return raw, None
    digits = re.sub(r"\D", "", raw)
    if digits.startswith("254"):
        digits = digits[3:]
    elif digits.startswith("0"):
        digits = digits[1:]
    phone = "+254" + digits
    return (phone, None) if KE_PHONE_RE.match(phone) else (raw, "invalid Kenyan phone number")


def clean_date(value):
    raw = clean_text(value)
    if not raw:
        return raw, None
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(raw, fmt).strftime("%Y-%m-%d"), None
        except ValueError:
            continue
    return raw, "unrecognised date format"


def column_rule(header):
    h = header.lower()
    if "phone" in h or "mobile" in h:
        return "phone"
    if "email" in h:
        return "email"
    if "date" in h or "dob" in h:
        return "date"
    if "name" in h:
        return "name"
    return "text"


def clean_file(src, dst, err_path):
    with open(src, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            sys.exit("Input file is empty or has no header row.")
        fields = [clean_text(h) for h in reader.fieldnames]
        rules = {orig: column_rule(orig) for orig in reader.fieldnames}
        rows_in = 0
        kept, seen, errors = [], set(), []
        stats = {"duplicates removed": 0, "blank rows removed": 0, "cells changed": 0}

        for line_no, row in enumerate(reader, start=2):
            rows_in += 1
            if not any(clean_text(v) for v in row.values() if v is not None):
                stats["blank rows removed"] += 1
                continue
            out = {}
            for orig, name in zip(reader.fieldnames, fields):
                before = row.get(orig) or ""
                rule = rules[orig]
                issue = None
                if rule == "phone":
                    after, issue = clean_phone(before)
                elif rule == "email":
                    after, issue = clean_email(before)
                elif rule == "date":
                    after, issue = clean_date(before)
                elif rule == "name":
                    after = clean_name(before)
                else:
                    after = clean_text(before)
                if after != before:
                    stats["cells changed"] += 1
                if issue:
                    errors.append({"row": line_no, "column": name, "value": before, "issue": issue})
                out[name] = after
            key = tuple(out.values())
            if key in seen:
                stats["duplicates removed"] += 1
                continue
            seen.add(key)
            kept.append(out)

    with open(dst, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(kept)
    with open(err_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["row", "column", "value", "issue"])
        writer.writeheader()
        writer.writerows(errors)

    print(f"Rows read:            {rows_in}")
    print(f"Rows written:         {len(kept)}")
    for label, n in stats.items():
        print(f"{label.capitalize():<22}{n}")
    print(f"Problems flagged:     {len(errors)}  (see {err_path})")
    print(f"Cleaned file:         {dst}")


def main():
    p = argparse.ArgumentParser(description="Clean a messy CSV file and report data problems.")
    p.add_argument("input", help="path to the CSV to clean")
    p.add_argument("-o", "--output", help="cleaned CSV path (default: <input>_cleaned.csv)")
    p.add_argument("-e", "--errors", help="errors CSV path (default: <input>_errors.csv)")
    a = p.parse_args()
    base = a.input.rsplit(".", 1)[0]
    clean_file(a.input, a.output or f"{base}_cleaned.csv", a.errors or f"{base}_errors.csv")


if __name__ == "__main__":
    main()
