from src.notifications.daily_summary_email import DailySummaryEmail


def test_daily_summary_email_smoke():
    rendered = DailySummaryEmail().render(["acct-1"])
    assert rendered["rows"][0]["account_id"] == "acct-1"
    assert rendered["invoices"][0]["status"] == "open"
