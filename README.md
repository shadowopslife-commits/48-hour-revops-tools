# 48-Hour RevOps Tools

Three practical Python tools for finding revenue leakage inside CRM exports—duplicate leads, inconsistent customer data, and opportunities that are not receiving timely follow-up.

These tools support focused revenue-recovery engagements for solar, healthcare, home-service, and professional-service businesses. They are dependency-free, run locally, and never transmit client data to a third party.

## Included tools

### `lead_deduper.py`

Finds duplicate leads using normalized email addresses and phone numbers. It writes a clean CSV and a separate duplicate-review report.

```bash
python lead_deduper.py leads.csv --clean clean_leads.csv --duplicates duplicate_leads.csv
```

### `crm_cleaner.py`

Normalizes names, emails, phone numbers, lifecycle stages, and state values while flagging records that need review.

```bash
python crm_cleaner.py crm_export.csv --output cleaned_crm.csv
```

### `followup_automator.py`

Scores open leads by age, engagement, estimated value, and stage, then produces a prioritized follow-up queue with recommended actions.

```bash
python followup_automator.py leads.csv --output followup_queue.csv
```

Run `python <script> --help` for field requirements and options. All processing is local; the scripts do not send data to third parties.

## Typical sprint workflow

1. Export contacts or opportunities from the CRM as CSV.
2. Preserve the original export unchanged.
3. Run the cleaner and review flagged rows.
4. Run the deduplicator and approve merges inside the CRM.
5. Generate the follow-up queue and assign owners.

## Important

Test against a copy of your export before importing results into a production CRM. Field mappings and business rules vary by organization.

## Need this implemented in your business?

I provide 48-hour CRM cleanup, dormant-pipeline recovery, workflow automation, and revenue-operations sprints.

**[Hire me on Upwork](https://www.upwork.com/freelancers/patricke22)**
