from src.billing.client import BillingClient
from src.reporting.service import ReportingService


class DailySummaryEmail:
    def __init__(self, reporting=None):
        self.reporting = reporting or ReportingService()

    def render(self, account_ids):
        report_rows = self.reporting.build_daily_summary(account_ids)
        invoices = []
        for account_id in account_ids:
            invoices.append(BillingClient().fetch_invoice(account_id))
        return {
            "rows": report_rows,
            "invoices": invoices,
        }
