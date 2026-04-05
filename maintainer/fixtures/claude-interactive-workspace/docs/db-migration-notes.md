# Database Migration Notes

- `accounts` remains the source of truth for account ownership.
- `invoices` currently stores status and amount inline.
- `ledger_entries` will be split out for append-only writes.
- `notifications` still references the old invoice status shape.
- Large migrations should preserve replayability and keep validation scripts in sync.
