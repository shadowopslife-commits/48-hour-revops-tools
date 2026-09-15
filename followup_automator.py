#!/usr/bin/env python3
"""Create a prioritized follow-up queue from a lead CSV."""

import argparse
import csv
from datetime import date, datetime
from pathlib import Path


STAGE_POINTS = {"proposal": 35, "qualified": 25, "contacted": 15, "new": 10}


def parse_date(value: str) -> date | None:
    for pattern in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y"):
        try:
            return datetime.strptime(value.strip(), pattern).date()
        except ValueError:
            pass
    return None


def score(row: dict[str, str], today: date) -> tuple[int, str]:
    points = STAGE_POINTS.get(row.get("stage", "").strip().lower(), 5)
    last_contact = parse_date(row.get("last_contacted", ""))
    age = (today - last_contact).days if last_contact else 30
    points += min(max(age, 0), 30)
    try:
        value = float(row.get("estimated_value", "0").replace(",", "").replace("$", ""))
    except ValueError:
        value = 0
    points += min(int(value / 1000) * 2, 25)
    engagement = row.get("engagement", "").strip().lower()
    points += {"high": 20, "medium": 10, "low": 3}.get(engagement, 0)
    action = "Call today" if points >= 70 else "Personal follow-up" if points >= 45 else "Sequence enrollment"
    return points, action


def process(source: Path, output: Path) -> int:
    with source.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("CSV must include a header row")
        fields = list(reader.fieldnames) + ["priority_score", "recommended_action"]
        rows = []
        for row in reader:
            points, action = score(row, date.today())
            enriched = dict(row)
            enriched["priority_score"] = str(points)
            enriched["recommended_action"] = action
            rows.append(enriched)
    rows.sort(key=lambda row: int(row["priority_score"]), reverse=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, default=Path("followup_queue.csv"))
    args = parser.parse_args()
    print(f"Prioritized records: {process(args.source, args.output)}")


if __name__ == "__main__":
    main()
