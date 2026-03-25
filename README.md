# The Compass

A bi-weekly self-calibration practice. Four questions. AI synthesis. A heading for the next two weeks.

---

Every two weeks, you sit down with The Compass.

You answer four questions:

1. **Evidence Log** — What did you build, ship, or complete that didn't exist before? Not learning. Not planning. Finishes.
2. **Drift Audit** — Where did your time go that wasn't consistent with your primary track? What was the real reason?
3. **Saboteur Signature** — Did your internal critic show up? In what specific behavioral form?
4. **Non-Negotiable** — One specific artifact that will exist two weeks from now that doesn't today.

Then Claude reads your responses against your personal context — your tracks, your time horizon, your known saboteur patterns — and synthesizes what's actually happening underneath the surface content.

It ends with a single sentence: the heading for the next two weeks. Not a plan. A direction.

---

## Two modes

**Bi-weekly (default)** — The regular rhythm. Four questions. 150–200 word synthesis. One heading.

**Quarterly** — The elevation view. A full-quarter audit: psychological state, strategic movement, what to release, current position. Harder. More honest. Uses recent bi-weekly sessions as context.

---

## Two interfaces

**CLI** (`compass.py`) — Terminal-native. Logs sessions to `~/.compass_sessions.jsonl`. Optional second brain integration.

**Web** (`compass_web.py`) — Stateless Flask app. No data stored server-side. Deploy behind nginx on your own VPS. Each session lives only in the browser.

---

## Setup

### Prerequisites

- Python 3.11+
- Anthropic API key (CLI uses Claude Opus)
- OpenAI API key (web interface)

### Install

```bash
git clone https://github.com/cousingary/compass
cd compass
pip install -r requirements.txt
cp .env.example .env
# edit .env with your keys
```

### First run (CLI)

```bash
python compass.py --setup
```

The setup wizard takes ~5 minutes. It captures your context, tracks, time horizon, saboteur signatures, and preferred synthesis tone. This shapes every future synthesis.

### Run a session

```bash
python compass.py                    # bi-weekly
python compass.py --mode quarterly   # quarterly
python compass.py --review           # review past sessions
```

### Web interface

```bash
python compass_web.py
# open http://localhost:5050
```

Deploy on a VPS:
```bash
PORT=8080 nohup python compass_web.py &
# configure nginx to proxy to 8080
```

### Bi-weekly reminder (cron)

```cron
0 9 * * 4 [ $(( $(date +\%W) \% 2 )) -eq 1 ] && python /path/to/compass/compass_remind.py
```

Writes a flag to `~/.compass_due`. Check it however you like.

---

## Configuration

The CLI stores config at `~/.compass_config.json`. Key fields:

```json
{
  "name": "Your name",
  "primary_context": "Who you are, what you're building, the core tension.",
  "primary_tracks": ["Track 1", "Track 2"],
  "time_horizon": "6 months",
  "saboteur_signatures": ["avoidance of highest-leverage work"],
  "psychological_phase": "building execution identity",
  "synthesis_tone": "direct"
}
```

Synthesis tones:
- `direct` — Peer-level, no hedging
- `supportive` — Honest but warm
- `clinical` — Neutral, analytical

The web interface takes the same fields as a form on each session — no persistent config server-side.

---

## Second brain integration

If you have a Supabase-backed second brain, Compass sessions can be ingested automatically. The CLI attempts to import `log_pipeline_output` from `~/second-brain/ingest.py`. If not found, it skips silently.

---

## The idea

Most productivity systems measure activity. The Compass measures signal.

The four questions are designed to cut through self-narration and surface what's actually happening: what got built (evidence), where alignment broke down (drift), how the internal critic showed up in behavioral form (saboteur), and what you're committing to next (non-negotiable).

The synthesis doesn't validate. It reads.

---

*Part of a personal AI infrastructure stack. Built for the intersection of structured practice and machine intelligence.*
