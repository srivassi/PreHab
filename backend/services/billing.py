import os
import uuid
from datetime import datetime

PAID_API_KEY = os.getenv("PAID_API_KEY", "")
AGENT_ID     = "prehab-agent"


def _get_or_create_order(client, athlete_id: str):
    """
    Get or create an order for the athlete.
    Signals need to be tied to an order in Paid.ai.
    """
    order_id = f"order_{athlete_id}_{datetime.now().strftime('%Y%m')}"  # Monthly order per athlete
    
    try:
        # Try to create/reference an order
        # Note: Paid.ai may auto-create orders, but we explicitly reference one here
        return order_id
    except Exception as e:
        print(f"[Paid.ai] Error getting/creating order: {e}")
        return None


def record_signal(event_name: str, athlete_id: str, risk_level: str, plan_adjusted: bool):
    """
    Record an agent signal to Paid.ai.
    IMPORTANT: Signals should be tied to an order to appear in billing.
    Silently skips if PAID_API_KEY is not set (e.g. during local dev).
    Also skips gracefully if paid-python is not installed or has issues.
    """
    if not PAID_API_KEY:
        print(f"[Paid.ai] PAID_API_KEY not set — skipping signal: {event_name}")
        return

    try:
        from paid import Paid, Signal, CustomerByExternalId  # pip install paid-python
    except ImportError as e:
        print(f"[Paid.ai] Import failed: {e}")
        return

    try:
        client = Paid(token=PAID_API_KEY)
        
        # Get or create an order (signals need an order to be attributed to)
        order_id = _get_or_create_order(client, athlete_id)
        if not order_id:
            print(f"[Paid.ai] Could not create order for {athlete_id}")
            return
        
        # Create signal with customer and order properly
        signal = Signal(
            event_name=event_name,
            agent_id=AGENT_ID,
            customer=CustomerByExternalId(externalCustomerId=athlete_id),
            order_id=order_id,
            data={
                "risk_level":    risk_level,
                "plan_adjusted": plan_adjusted,
                "costData": {
                    "vendor": "crusoe",
                    "cost": {"amount": 0.002, "currency": "USD"},
                }
            }
        )
        client.signals.create_signals(signals=[signal])
        print(f"[Paid.ai] Signal recorded: {event_name} for {athlete_id}")

    except Exception as e:
        print(f"[Paid.ai] Failed to record signal: {e}")

