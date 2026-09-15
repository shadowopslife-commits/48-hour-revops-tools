#!/usr/bin/env python3
"""Normalize common fields in a CRM CSV export."""

import argparse
import csv
import re
from pathlib import Path


STAGES = {
    "new lead": "New",
    "new": "New",
    "contacted": "Contacted",
    "qualified": "Qualified",
    "proposal": "Proposal",
    "won": "Won",
    "closed won": "Won",
    "lost": "Lost",
    "closed lost": "Lost",
}


def clean_phone(value: str) -> str:
    digits = re.sub(r"\D", "", value)
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}" if len(digits) == 10 else value.strip()


def clean_row(row: dict[str, str]) -> dict[str, str]:
    result = {key: (value or "").strip() for key, value in row.items()}
    flags: list[str] = []
    for field in ("first_name", "last_name"):
        if field in result:
            result[field] = result[field].title()
    if "email" in result:
        result["email"] = result["email"].lower()
        if result["email"] and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", result["email"]):
            flags.append("invalid_email")
    if "phone" in result:
        original = result["phone"]
        result["phone"] = clean_phone(original)
        if original and len(re.sub(r"\D", "", original)) not in (10, 11):
            flags.append("invalid_phone")
    if "stage" in result:
        raw_stage = result["stage"].lower()
        if raw_stage:
            result["stage"] = STAGES.get(raw_stage, result["stage"].title())
            if raw_stage not in STAGES:
                flags.append("review_stage")
    if "state" in result:
        result["state"] = result["state"].upper()
    result["review_flags"] = ";".join(flags)
    return result


def process(source: Path, output: Path) -> tuple[int, int]:
    with source.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("CSV must include a header row")
        fields = list(reader.fieldnames) + ["review_flags"]
        rows = [clean_row(row) for row in reader]
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return len(rows), sum(bool(row["review_flags"]) for row in rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, default=Path("cleaned_crm.csv"))
    args = parser.parse_args()
    count, flagged = process(args.source, args.output)
    print(f"Cleaned records: {count}; records requiring review: {flagged}")


if __name__ == "__main__":
    main()
