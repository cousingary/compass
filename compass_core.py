"""
compass_core.py — Shared synthesis logic for compass.py and compass_web.py
"""

import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-opus-4-6"

_client = None

def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    return _client


TONE_INSTRUCTIONS = {
    "direct":    "Peer-level. No hedging. No cheerleading. If something is concerning, name it precisely. If something is genuine progress, name it precisely — not effusively.",
    "supportive":"Warm but honest. Acknowledge effort while surfacing patterns clearly. Don't soften the signal, but frame it constructively.",
    "clinical":  "Neutral, analytical. Describe what the data shows without editorial. Leave interpretation to the user.",
}


def build_biweekly_system_prompt(config: dict) -> str:
    context    = config.get("primary_context", "")
    tracks     = config.get("primary_tracks", [])
    horizon    = config.get("time_horizon", "")
    saboteurs  = config.get("saboteur_signatures", [])
    phase      = config.get("psychological_phase", "")
    tone       = config.get("synthesis_tone", "direct")

    tracks_str    = "\n".join(f"- {t}" for t in tracks)    if tracks    else "- Not specified"
    saboteurs_str = "\n".join(f"- {s}" for s in saboteurs) if saboteurs else "- Not yet identified"
    tone_str      = TONE_INSTRUCTIONS.get(tone, TONE_INSTRUCTIONS["direct"])

    prompt = f"""You are the Compass — a synthesis and reflection engine supporting a structured self-calibration practice.

CONTEXT ON THIS USER:
{context}

PRIMARY TRACKS (what they are building toward):
{tracks_str}

TIME HORIZON: {horizon if horizon else "Not specified"}

KNOWN SABOTEUR SIGNATURES (how their internal critic typically shows up):
{saboteurs_str}
"""

    if phase:
        prompt += f"\nCURRENT PSYCHOLOGICAL PHASE:\n{phase}\n"

    prompt += f"""
YOUR FUNCTION IN THIS SESSION:
1. Read the raw responses provided across the four questions.
2. Identify the real signal underneath the surface content — what is actually being reported vs. what is being named.
3. Surface patterns the person may not be naming directly.
4. For the saboteur question: be precise about the specific behavioral form it took this cycle.
5. For the non-negotiable: assess whether it is specific enough to be meaningful. If it's vague, name that.
6. Produce a synthesis of 150–200 words.

TONE: {tone_str}

End with a single sentence — the heading for the next session. Not a goal list. A direction."""

    return prompt


def build_quarterly_system_prompt(config: dict) -> str:
    context   = config.get("primary_context", "")
    tracks    = config.get("primary_tracks", [])
    saboteurs = config.get("saboteur_signatures", [])

    tracks_str    = "\n".join(f"- {t}" for t in tracks)    if tracks    else "- Not specified"
    saboteurs_str = "\n".join(f"- {s}" for s in saboteurs) if saboteurs else "- Not yet identified"

    return f"""You are the Compass in Quarterly Calibration mode.

This is the elevation view — a full-quarter audit of psychological and strategic state.

CONTEXT ON THIS USER:
{context}

PRIMARY TRACKS:
{tracks_str}

KNOWN SABOTEUR SIGNATURES:
{saboteurs_str}

YOUR FUNCTION:
1. A direct assessment of the quarter's psychological state — what version of this person was operating? Where did old limiting patterns appear in disguised form?
2. A strategic read — what moved, what didn't, and the honest reason.
3. A single paragraph stating where this person actually is — not where they hoped to be.
4. The heading for the next quarter — one clear direction, not a plan.

Be harder here than in the daily sessions. Quarterly calibration is the moment for full honesty.
Patterns that appeared as isolated data points in individual sessions become signal at this scale."""


def synthesize(system_prompt: str, session_text: str, max_tokens: int = 600) -> str:
    client = get_client()
    message = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": session_text}]
    )
    return message.content[0].text


def build_biweekly_session_text(responses: dict) -> str:
    text = f"""COMPASS SESSION — {responses.get('session_date', '')}

EVIDENCE LOG (what was built/shipped/completed):
{responses.get('evidence_log', '')}

DRIFT AUDIT (where time was misaligned, real reason):
{responses.get('drift_audit', '')}

SABOTEUR SIGNATURE (how the internal critic showed up):
{responses.get('saboteur_signature', '')}

NON-NEGOTIABLE (specific output committed to for next session):
{responses.get('non_negotiable', '')}
"""
    if responses.get("signal_note"):
        text += f"\nSIGNAL / RECURRING PATTERN:\n{responses['signal_note']}\n"
    return text


def build_quarterly_session_text(responses: dict, context_block: str = "") -> str:
    return f"""QUARTERLY COMPASS CALIBRATION — {responses.get('session_date', '')}

PSYCHOLOGICAL REVIEW:
{responses.get('psychological_review', '')}

STRATEGIC REVIEW:
{responses.get('strategic_review', '')}

RELEASE AUDIT:
{responses.get('release_audit', '')}

CURRENT POSITION STATEMENT:
{responses.get('current_position', '')}
{context_block}"""
