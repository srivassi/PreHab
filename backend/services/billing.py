import os

PAID_API_KEY = os.getenv("PAID_API_KEY", "")
AGENT_ID     = "prehab-agent"


def record_signal(event_name: str, athlete_id: str, risk_level: str, plan_adjusted: bool):
    """
    Record an agent signal to Paid.ai.
    Silently skips if PAID_API_KEY is not set (e.g. during local dev).
    """
    if not PAID_API_KEY:
        print(f"[Paid.ai] PAID_API_KEY not set — skipping signal: {event_name}")
        return

    try:
        from paid import Paid, Signal  # pip install paid-python

        client = Paid(token=PAID_API_KEY)
        signal = Signal(
            event_name=event_name,
            agent_id=AGENT_ID,
            customer_id=athlete_id,
            data={
                "risk_level":    risk_level,
                "plan_adjusted": plan_adjusted,
                "costData": {
                    "vendor": "crusoe",
                    "cost": {"amount": 0.002, "currency": "USD"},
                }
            }
        )
        client.usage.record_bulk(signals=[signal])
        print(f"[Paid.ai] Signal recorded: {event_name} for {athlete_id}")

    except Exception as e:
        print(f"[Paid.ai] Failed to record signal: {e}")
