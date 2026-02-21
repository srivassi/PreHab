from datetime import date, datetime


PHASE_NAMES = {0: "menstrual", 1: "follicular", 2: "ovulatory", 3: "luteal"}


def infer_current_phase(cycle_start_date: str, cycle_length: int, menstruation_length: int) -> dict:
    """
    Infer the current menstrual phase based on cycle start date.

    Phases (approximate):
      0 - Menstrual:   day 1 → menstruation_length
      1 - Follicular:  menstruation_length+1 → cycle_length * 0.45
      2 - Ovulatory:   around day 14 (±2 days)
      3 - Luteal:      day 15 → cycle_length
    """
    try:
        start = datetime.strptime(cycle_start_date, "%Y-%m-%d").date()
    except ValueError:
        return {"phase_int": 1, "phase_name": "follicular", "day_of_cycle": None}

    today = date.today()
    day_of_cycle = ((today - start).days % cycle_length) + 1

    ovulation_day = round(cycle_length * 0.45)

    if day_of_cycle <= menstruation_length:
        phase = 0
    elif day_of_cycle < ovulation_day - 1:
        phase = 1
    elif day_of_cycle <= ovulation_day + 2:
        phase = 2
    else:
        phase = 3

    return {
        "phase_int":    phase,
        "phase_name":   PHASE_NAMES[phase],
        "day_of_cycle": day_of_cycle,
    }

