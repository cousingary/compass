"""
compass_web.py — Web interface for The Compass

A stateless Flask app. Users fill in their context + 4 session responses,
submit, and receive synthesis on-page. No data is stored server-side.

Run:
    python compass_web.py              # port 5050
    PORT=8080 python compass_web.py    # custom port

Deploy behind nginx or any reverse proxy.
"""

import os
from datetime import datetime, timezone
from flask import Flask, render_template, request
from dotenv import load_dotenv
import openai

load_dotenv()

try:
    from compass_core import build_biweekly_system_prompt, build_biweekly_session_text
except ImportError:
    raise RuntimeError("compass_core.py must be in the same directory as compass_web.py")

WEB_MODEL = os.getenv("COMPASS_WEB_MODEL", "gpt-4o")
_openai_client = None

def _get_openai_client():
    global _openai_client
    if _openai_client is None:
        _openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _openai_client

def synthesize_openai(system_prompt: str, session_text: str, max_tokens: int = 600) -> str:
    client = _get_openai_client()
    response = client.chat.completions.create(
        model=WEB_MODEL,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": session_text},
        ],
    )
    return response.choices[0].message.content

app = Flask(__name__)


def _config_from_form(form) -> dict:
    raw_tracks    = form.get("primary_tracks", "").strip()
    raw_saboteurs = form.get("saboteur_signatures", "").strip()
    tracks    = [t.strip() for t in raw_tracks.splitlines()    if t.strip()]
    saboteurs = [s.strip() for s in raw_saboteurs.splitlines() if s.strip()]
    return {
        "name":                 form.get("name", "").strip() or "User",
        "primary_context":      form.get("primary_context", "").strip(),
        "primary_tracks":       tracks,
        "time_horizon":         form.get("time_horizon", "").strip(),
        "saboteur_signatures":  saboteurs,
        "psychological_phase":  form.get("psychological_phase", "").strip(),
        "synthesis_tone":       form.get("synthesis_tone", "direct"),
    }


@app.route("/", methods=["GET"])
def index():
    return render_template("compass_form.html")


@app.route("/synthesize", methods=["POST"])
def synthesize_session():
    config = _config_from_form(request.form)

    responses = {
        "session_date":       datetime.now(timezone.utc).isoformat(),
        "evidence_log":       request.form.get("evidence_log", "").strip(),
        "drift_audit":        request.form.get("drift_audit", "").strip(),
        "saboteur_signature": request.form.get("saboteur_signature", "").strip(),
        "non_negotiable":     request.form.get("non_negotiable", "").strip(),
    }

    missing = [k for k in ("evidence_log", "drift_audit", "saboteur_signature", "non_negotiable")
               if not responses[k]]
    if missing:
        return render_template(
            "compass_form.html",
            error="Please complete all four session fields.",
            prefill=dict(request.form),
        ), 400

    try:
        synthesis = synthesize_openai(
            system_prompt=build_biweekly_system_prompt(config),
            session_text=build_biweekly_session_text(responses),
            max_tokens=600,
        )
        error = None
    except Exception as e:
        synthesis = None
        error = f"Synthesis failed: {e}"

    return render_template(
        "compass_result.html",
        synthesis=synthesis,
        error=error,
        name=config["name"],
        non_negotiable=responses["non_negotiable"],
        session_date=responses["session_date"][:10],
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5050))
    app.run(host="0.0.0.0", port=port)
