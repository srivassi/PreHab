import os
import json
import openai

CRUSOE_API_KEY  = os.getenv("CRUSOE_API_KEY", "")
CRUSOE_BASE_URL = "https://api.crusoe.ai/v1"
QWEN_MODEL      = os.getenv("QWEN_MODEL", "qwen3-235b-a22b-instruct-2507")  # update with exact Crusoe model string


def generate(analysis: dict) -> str:
    """
    Call Crusoe (Qwen) with the full analysis blob.
    Returns a plain-English explanation for the athlete.
    Falls back to a template string if API call fails.
    """
    if not CRUSOE_API_KEY:
        return _template_fallback(analysis)

    try:
        client = openai.OpenAI(
            api_key=CRUSOE_API_KEY,
            base_url=CRUSOE_BASE_URL,
        )

        prompt = f"""You are PreHab's injury prevention agent for female athletes.

Here is the athlete's full risk analysis:
{json.dumps(analysis, indent=2)}

Write a clear, empathetic 3-4 sentence explanation for the athlete that covers:
- What her main risks are this week and why (use specific numbers)
- What has been changed in her training plan and why
- What she should watch for over the next few days

Tone: knowledgeable physio, warm but direct. No bullet points. Plain paragraph."""

        response = client.chat.completions.create(
            model=QWEN_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"[Crusoe] API call failed: {e}")
        return _template_fallback(analysis)


def _template_fallback(analysis: dict) -> str:
    """Rule-based fallback explanation if Crusoe is unavailable."""
    risk   = analysis.get("composite_risk_level", "MEDIUM")
    ratio  = analysis.get("trend_analysis", {}).get("acute_chronic_ratio", 0)
    phase  = analysis.get("trend_analysis", {}).get("cycle_risk_window", "")
    top    = analysis.get("contributing_factors", [{}])[0].get("label", "training load")
    actions = analysis.get("recommended_actions", [])

    action_text = ""
    if "reduce_plyometrics" in actions:
        action_text += "We've reduced your plyometric volume this week. "
    if "add_stability" in actions:
        action_text += "Stability work has been added to support your joints. "
    if "reduce_sprint_intensity" in actions:
        action_text += "Sprint intensity has been lowered. "

    return (
        f"Your injury risk is currently {risk.lower()} (load ratio: {ratio:.2f}). "
        f"The primary driver is {top.lower()}. "
        f"{action_text}"
        f"Monitor soreness closely over the next 3 days and rest if anything worsens."
    )
