#!/usr/bin/env python3
"""Find duplicate CRM leads in a CSV export."""

import argparse
import csv
import re
from pathlib import Path


def normalize_email(value: str) -> str:
    return value.strip().lower()


def normalize_phone(value: str) -> str:
    digits = re.sub(r"\D", "", value)
    return digits[-10:] if len(digits) >= 10 else digits


def duplicate_key(row: dict[str, str]) -> tuple[str, str] | None:
    email = normalize_email(row.get("email", ""))
    phone = normalize_phone(row.get("phone", ""))
    if email:
        return ("email", email)
    if phone:
        return ("phone", phone)
    return None


def process(source: Path, clean_path: Path, duplicates_path: Path) -> tuple[int, int]:
    with source.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("CSV must include a header row")
        rows = list(reader)
        fields = list(reader.fieldnames)

    seen: dict[tuple[str, str], int] = {}
    clean: list[dict[str, str]] = []
    duplicates: list[dict[str, str]] = []

    for source_row, row in enumerate(rows, start=2):
        key = duplicate_key(row)
        if key is not None and key in seen:
            duplicate = dict(row)
            duplicate["duplicate_reason"] = key[0]
            duplicate["duplicate_of_csv_row"] = str(seen[key])
            duplicates.append(duplicate)
            continue
        if key is not None:
            seen[key] = source_row
        clean.append(row)

    with clean_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(clean)

    duplicate_fields = fields + ["duplicate_reason", "duplicate_of_csv_row"]
    with duplicates_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=duplicate_fields)
        writer.writeheader()
        writer.writerows(duplicates)

    return len(clean), len(duplicates)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--clean", type=Path, default=Path("clean_leads.csv"))
    parser.add_argument("--duplicates", type=Path, default=Path("duplicate_leads.csv"))
    args = parser.parse_args()
    clean_count, duplicate_count = process(args.source, args.clean, args.duplicates)
    print(f"Clean records: {clean_count}; duplicates flagged: {duplicate_count}")


if __name__ == "__main__":
    main()
