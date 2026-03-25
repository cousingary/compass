#!/usr/bin/env python3
"""
THE COMPASS — Bi-Weekly Self-Calibration Pipeline
Synthesizes your work and psychological state using Claude. Logs to local JSONL
and optionally to a Supabase second brain.

Usage:
  python compass.py                   # run bi-weekly session
  python compass.py --mode quarterly  # run quarterly deep-calibration
  python compass.py --review          # review past sessions
  python compass.py --setup           # run first-time setup wizard
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

CONFIG_FILE = os.path.expanduser("~/.compass_config.json")
SESSION_LOG = os.path.expanduser("~/.compass_sessions.jsonl")

try:
    from compass_core import (
        build_biweekly_system_prompt, build_quarterly_system_prompt,
        build_biweekly_session_text, build_quarterly_session_text,
        synthesize,
    )
except ImportError:
    print("compass_core.py not found. Ensure it is in the same directory.")
    sys.exit(1)

try:
    sys.path.append(os.path.expanduser("~/second-brain"))
    from ingest import log_pipeline_output
    SECOND_BRAIN_AVAILABLE = True
except ImportError:
    SECOND_BRAIN_AVAILABLE = False

try:
    import anthropic  # noqa: F401
except ImportError:
    print("anthropic package not found. Run: pip install anthropic")
    sys.exit(1)


DEFAULT_CONFIG = {
    "name": "User",
    "primary_context": "A person working toward meaningful goals.",
    "primary_tracks": [],
    "time_horizon": "6 months",
    "saboteur_signatures": [],
    "psychological_phase": "",
    "synthesis_tone": "direct",
    "optional_signal_field": True,
    "second_brain_project": "personal_development"
}


def load_config() -> dict:
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return {**DEFAULT_CONFIG, **json.load(f)}
    return DEFAULT_CONFIG.copy()


def save_config(config: dict):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def run_setup_wizard():
    print("\n" + "═" * 60)
    print("  THE COMPASS — First-Time Setup")
    print("═" * 60)
    print("""
  This wizard builds your personal configuration file.
  It takes about 5 minutes and shapes how the Compass reads
  your sessions. You can edit ~/.compass_config.json any time.
""")

    config = {}

    print("  What should the Compass call you?")
    config["name"] = input("  > ").strip() or "User"

    print("""
  Describe your current situation in 2–4 sentences.
  Who are you, what are you building, what's the core tension?
  This is the context that shapes every synthesis.
  (Press Enter twice when done)
""")
    config["primary_context"] = multiline_input("").strip()

    print("""
  What are your 1–3 primary tracks right now?
  These are the things you are actively building toward —
  not values or aspirations, concrete directions.
  Enter each on its own line. Blank line to finish.
""")
    tracks = []
    while True:
        t = input("  > ").strip()
        if not t:
            break
        tracks.append(t)
    config["primary_tracks"] = tracks

    print("""
  What is your primary time horizon?
  (e.g. "6 months", "1 year", "end of Q3 2026")
""")
    config["time_horizon"] = input("  > ").strip()

    print("""
  How does your internal critic typically show up?
  These are behavioral patterns — not feelings, but actions.
  Examples: "avoidance of highest-leverage work",
            "overengineering before validating",
            "seeking approval before shipping"
  Enter each on its own line. Blank line to finish.
""")
    saboteurs = []
    while True:
        s = input("  > ").strip()
        if not s:
            break
        saboteurs.append(s)
    config["saboteur_signatures"] = saboteurs

    print("""
  Optionally: describe where you are psychologically right now.
  Not a mood — a phase. Examples: "clearing old conditioning",
  "building execution identity", "consolidating gains". (Enter to skip)
""")
    config["psychological_phase"] = input("  > ").strip()

    print("""
  What synthesis tone do you want?

  1. direct     — Peer-level, no hedging, no softening
  2. supportive — Honest but warm, constructive framing
  3. clinical   — Neutral, analytical, minimal editorial

""")
    tone_choice = input("  > ").strip()
    config["synthesis_tone"] = {"1": "direct", "2": "supportive", "3": "clinical"}.get(tone_choice, "direct")

    print("""
  Include an optional dream / signal field at the end of each session?
  A space to note recurring patterns, significant dreams, intuitive signals. (y/n, default: y)
""")
    sig_choice = input("  > ").strip().lower()
    config["optional_signal_field"] = sig_choice != "n"

    print("""
  If you're using a Supabase second brain, what project tag
  should Compass sessions be filed under?
  (default: personal_development)
""")
    project_tag = input("  > ").strip()
    config["second_brain_project"] = project_tag or "personal_development"

    save_config(config)

    print(f"""
{"═" * 60}
  Setup complete. Config saved to ~/.compass_config.json

  Your primary tracks:""")
    for t in config.get("primary_tracks", []):
        print(f"    → {t}")
    print(f"""
  Synthesis tone: {config['synthesis_tone']}
  Time horizon:   {config.get('time_horizon', 'not set')}

  Run your first session:
    python compass.py
{"═" * 60}
""")


def print_header(text, char="─"):
    width = 60
    print(f"\n{char * width}")
    print(f"  {text}")
    print(f"{char * width}\n")


def multiline_input(prompt="") -> str:
    if prompt:
        print(f"  {prompt}")
    print("  (Press Enter twice when done)\n")
    lines = []
    while True:
        line = input("  > ")
        if line == "" and lines and lines[-1] == "":
            break
        lines.append(line)
    return "\n".join(lines).strip()


def single_input(prompt="") -> str:
    if prompt:
        print(f"  {prompt}")
    return input("  > ").strip()


def run_biweekly_session(config: dict) -> dict:
    print_header("THE COMPASS — Daily Session", "═")
    print(f"  {datetime.now().strftime('%A, %B %d, %Y')}")
    print(f"  Session type: Daily Ritual\n")

    responses = {
        "session_date": datetime.now(timezone.utc).isoformat(),
        "session_type": "biweekly",
    }

    print_header("1 / 4  —  EVIDENCE LOG")
    print("  What did you build, ship, or complete since your last session")
    print("  that didn't exist before? Verifiable outputs only.")
    print("  Not learning, not planning, not starting. Finishes.\n")
    responses["evidence_log"] = multiline_input()

    print_header("2 / 4  —  DRIFT AUDIT")
    print("  Where did you spend time that wasn't consistent with your")
    print("  primary track? What was the real reason?\n")
    responses["drift_audit"] = multiline_input()

    print_header("3 / 4  —  SABOTEUR SIGNATURE")
    print("  Did the internal critic show up today or since last session?")
    print("  In what specific behavioral form?\n")
    responses["saboteur_signature"] = multiline_input()

    print_header("4 / 4  —  NON-NEGOTIABLE")
    print("  One specific output that will exist at your next session")
    print("  that doesn't exist today. Not a task. An artifact.\n")
    responses["non_negotiable"] = single_input()

    if config.get("optional_signal_field", True):
        print_header("OPTIONAL  —  SIGNAL / RECURRING PATTERN")
        print("  Any significant dream, recurring pattern, or intuitive signal? (Enter to skip)\n")
        signal = input("  > ").strip()
        if signal:
            responses["signal_note"] = signal

    print_header("SYNTHESIZING", "·")
    print("  Running synthesis...\n")

    try:
        synthesis = synthesize(
            system_prompt=build_biweekly_system_prompt(config),
            session_text=build_biweekly_session_text(responses),
            max_tokens=600,
        )
    except Exception as e:
        synthesis = f"[Synthesis unavailable: {e}]"

    responses["synthesis"] = synthesis
    print_header("COMPASS SYNTHESIS", "═")
    print(synthesis)
    print()
    return responses


def run_quarterly_session(config: dict) -> dict:
    print_header("THE COMPASS — Quarterly Calibration", "═")
    print(f"  {datetime.now().strftime('%A, %B %d, %Y')}")
    print(f"  Session type: Quarterly Audit\n")

    responses = {
        "session_date": datetime.now(timezone.utc).isoformat(),
        "session_type": "quarterly",
    }

    recent = load_recent_sessions(n=6)
    context_block = ""
    if recent:
        context_block = "\n\nRECENT SESSION SUMMARIES:\n"
        for s in recent:
            date = s.get("session_date", "")[:10]
            evidence = s.get("evidence_log", "")[:200]
            saboteur = s.get("saboteur_signature", "")[:150]
            context_block += f"\n[{date}]\n  Evidence: {evidence}\n  Saboteur: {saboteur}\n"

    print_header("PSYCHOLOGICAL REVIEW")
    print("  What version of yourself were you operating from this quarter?\n")
    responses["psychological_review"] = multiline_input()

    print_header("STRATEGIC REVIEW")
    print("  What moved toward your primary tracks? What didn't, and why honestly?\n")
    responses["strategic_review"] = multiline_input()

    print_header("WHAT TO RELEASE")
    print("  Which activities would you be ashamed to still be doing in 6 months?\n")
    responses["release_audit"] = multiline_input()

    print_header("CURRENT POSITION")
    print("  State where you actually are — not where you hoped to be.\n")
    responses["current_position"] = multiline_input()

    print_header("SYNTHESIZING", "·")
    print("  Running quarterly synthesis...\n")

    try:
        synthesis = synthesize(
            system_prompt=build_quarterly_system_prompt(config),
            session_text=build_quarterly_session_text(responses, context_block),
            max_tokens=800,
        )
    except Exception as e:
        synthesis = f"[Synthesis unavailable: {e}]"

    responses["synthesis"] = synthesis
    print_header("QUARTERLY SYNTHESIS", "═")
    print(synthesis)
    print()
    return responses


def save_session(responses: dict):
    with open(SESSION_LOG, "a") as f:
        f.write(json.dumps(responses) + "\n")
    print(f"  ✓ Session logged → {SESSION_LOG}")


def ingest_to_second_brain(responses: dict, config: dict):
    if not SECOND_BRAIN_AVAILABLE:
        return

    project = config.get("second_brain_project", "personal_development")
    session_type = responses.get("session_type", "biweekly")
    date_str = responses.get("session_date", "")[:10]

    content = f"""COMPASS SESSION [{session_type.upper()}] — {date_str}

EVIDENCE LOG:
{responses.get('evidence_log', '')}

DRIFT AUDIT:
{responses.get('drift_audit', '')}

SABOTEUR SIGNATURE:
{responses.get('saboteur_signature', '')}

NON-NEGOTIABLE / POSITION:
{responses.get('non_negotiable', responses.get('current_position', ''))}

SYNTHESIS:
{responses.get('synthesis', '')}
"""
    if responses.get("signal_note"):
        content += f"\nSIGNAL NOTE:\n{responses['signal_note']}\n"

    try:
        log_pipeline_output(
            content=content,
            pipeline_name="compass",
            project=project,
            extra_metadata={
                "session_type": session_type,
                "session_date": responses.get("session_date"),
                "non_negotiable": responses.get("non_negotiable", ""),
            }
        )
        print("  ✓ Session ingested to second brain")
    except Exception as e:
        print(f"  ✗ Second brain ingest failed: {e}")


def load_recent_sessions(n: int = 6) -> list:
    if not os.path.exists(SESSION_LOG):
        return []
    sessions = []
    with open(SESSION_LOG) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    sessions.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return sessions[-n:]


def review_sessions():
    sessions = load_recent_sessions(n=10)
    if not sessions:
        print("\n  No sessions found. Run: python compass.py\n")
        return

    print_header("COMPASS SESSION HISTORY", "═")
    for s in reversed(sessions):
        date = s.get("session_date", "")[:10]
        stype = s.get("session_type", "biweekly").upper()
        committed = s.get("non_negotiable", s.get("current_position", ""))[:80]
        synthesis_preview = s.get("synthesis", "")[:120]
        print(f"  [{date}] {stype}")
        if committed:
            print(f"  Committed:  {committed}...")
        if synthesis_preview:
            print(f"  Synthesis:  {synthesis_preview}...")
        print()


def main():
    parser = argparse.ArgumentParser(description="The Compass — Bi-Weekly Self-Calibration")
    parser.add_argument("--mode", choices=["biweekly", "quarterly"], default="biweekly")
    parser.add_argument("--review", action="store_true")
    parser.add_argument("--setup",  action="store_true")
    args = parser.parse_args()

    if args.setup:
        run_setup_wizard()
        return

    if args.review:
        review_sessions()
        return

    if not os.path.exists(CONFIG_FILE):
        print("\n  No config found. Running setup wizard first...\n")
        run_setup_wizard()

    config = load_config()

    if args.mode == "quarterly":
        responses = run_quarterly_session(config)
    else:
        responses = run_biweekly_session(config)

    print_header("SAVING")
    save_session(responses)
    ingest_to_second_brain(responses, config)

    print()
    print_header("SESSION COMPLETE", "═")
    print("  Your non-negotiable is logged. It will be waiting.\n")


if __name__ == "__main__":
    main()
