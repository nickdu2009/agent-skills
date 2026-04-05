from src.billing.client import BillingClient


class ReportingService:
    def __init__(self, billing_client=None):
        self.billing_client = billing_client or BillingClient()

    def build_daily_summary(self, account_ids):
        rows = []
        for account_id in account_ids:
            invoice = self.billing_client.fetch_invoice(account_id)
            rows.append(
                {
                    "account_id": account_id,
                    "invoice_amount": invoice["amount"],
                    "status": invoice["status"],
                }
            )
        return rows
