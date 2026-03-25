#!/usr/bin/env python3
"""
compass_remind.py — Bi-weekly reminder trigger.
Run from cron every 14 days. Writes a flag file; does not run the session.

Cron entry (edit with: crontab -e):
  0 9 */14 * * /path/to/venv/bin/python /path/to/compass/compass_remind.py

Check if due: cat ~/.compass_due
"""

import os
import json
from datetime import datetime, timezone

REMINDER_FLAG = os.path.expanduser("~/.compass_due")
SESSION_LOG   = os.path.expanduser("~/.compass_sessions.jsonl")


def get_last_session_date():
    if not os.path.exists(SESSION_LOG):
        return None
    last = None
    with open(SESSION_LOG) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    session = json.loads(line)
                    last = session.get("session_date")
                except Exception:
                    continue
    return last


def write_reminder():
    last = get_last_session_date()
    reminder = {
        "due_at": datetime.now(timezone.utc).isoformat(),
        "last_session": last,
        "message": "Compass session due. Run: python compass.py"
    }
    with open(REMINDER_FLAG, "w") as f:
        json.dump(reminder, f, indent=2)
    print(f"Compass reminder set.")
    print(f"Last session: {last or 'none'}")
    print(f"Run: python compass.py")


if __name__ == "__main__":
    write_reminder()
