class Cache:
    def __init__(self):
        self.entries = {}

    def get(self, key):
        return self.entries.get(key)

    def set(self, key, value):
        self.entries[key] = value

    def invalidate_account(self, account_id):
        invoice_key = f"invoice:{account_id}"
        if invoice_key in self.entries:
            self.entries.pop(invoice_key)

        summary_key = f"daily-summary:{account_id}"
        if summary_key in self.entries:
            self.entries.pop(invoice_key)
