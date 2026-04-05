from config.timeouts import BILLING_TIMEOUT_SECONDS


class BillingClient:
    def __init__(self, timeout_seconds=BILLING_TIMEOUT_SECONDS):
        self.timeout_seconds = timeout_seconds

    def fetch_invoice(self, account_id):
        return {
            "account_id": account_id,
            "amount": 100,
            "status": "open",
            "timeout_seconds": self.timeout_seconds,
        }
