# The Compass

*A bi-weekly self-calibration practice, synthesized by AI.*

---

Most systems measure activity.

The Compass measures signal.

---

## What It Is

Every two weeks, you sit down with The Compass. You answer four questions. There is no dashboard, no streak counter, no gamification. There is only what you built, where you drifted, how the critic showed up, and what you're committing to next.

Then Claude reads your answers — not against a productivity framework, but against you. Against your stated tracks, your known time horizon, your identified saboteur patterns. It looks for what's actually being reported underneath what's being said. It names things you didn't name. It ends with a single sentence: the heading for the next two weeks. Not a plan. A direction.

You do this every fourteen days.

---

## The Four Questions

**1. Evidence Log**
What did you build, ship, or complete in the past two weeks that didn't exist before?
*Not learning. Not planning. Not starting. Finishes.*

**2. Drift Audit**
Where did your time go that wasn't consistent with your primary track?
*What was the real reason.*

**3. Saboteur Signature**
Did your internal critic show up? In what specific behavioral form?
*Not a feeling. A behavior. Avoidance of highest-leverage work. Overengineering before validating. Seeking approval before shipping. The critic doesn't announce itself — it shows up wearing a different face every cycle. Name the face.*

**4. The Non-Negotiable**
One specific artifact that will exist two weeks from now that doesn't exist today.
*Not a task. Not a commitment to try. An artifact.*

---

## Why These Four

The Evidence Log is the only question that can't be faked. You either built it or you didn't.

The Drift Audit is the honesty question. The "real reason" qualifier is load-bearing. Without it, you get a description of what happened. With it, you sometimes get the thing underneath — the pattern that's been running for years, just in a different costume.

The Saboteur Signature is the hardest question and the most important. The internal critic doesn't show up as a feeling of inadequacy. It shows up as a decision to reorganize files instead of shipping. It shows up as three hours of research that was really avoidance. It shows up as picking a fight the night before a deadline. Name the specific behavioral form it took this cycle. Over months, you start to see the pattern. The pattern is useful.

The Non-Negotiable is a bridge. It exists so that the session isn't just reflection — it's a commitment the next session will audit. The system has memory. What you say here will be waiting.

---

## The Synthesis

After you answer the four questions, Claude reads them.

Not to validate. Not to encourage. To synthesize — to find the signal underneath the surface content, surface patterns you aren't naming, and assess whether your non-negotiable is specific enough to actually be meaningful. (Vague non-negotiables are named as vague. This is by design.)

Three synthesis tones are available:

- **Direct** — Peer-level. No hedging. No softening. If something is concerning, it's named precisely. If something is genuine progress, that's named precisely too — not effusively.
- **Supportive** — Honest but warm. The signal is surfaced, not softened.
- **Clinical** — Neutral. Analytical. Describes what the data shows. Leaves interpretation to you.

The synthesis ends with a single sentence. The heading for the next two weeks. You don't get a to-do list. You get a direction.

---

## Two Sessions

**Bi-weekly** — The regular rhythm. Four questions. Synthesis. Heading. Repeat.

**Quarterly** — The elevation view. Once a quarter, you audit the quarter itself: what version of you was operating, what moved strategically, what you'd be ashamed to still be doing in six months, and where you actually are versus where you thought you'd be. The quarterly synthesis is harder. It's supposed to be. Patterns that appeared as isolated data points across bi-weekly sessions become visible signal at this scale.

The quarterly session reads recent bi-weekly sessions as context. It looks for recurrence. What showed up once is an event. What showed up six times is a pattern. The synthesis names patterns.

---

## Two Interfaces

**CLI** (`compass.py`) — Terminal-native. Logs every session to `~/.compass_sessions.jsonl`. Optional integration with a Supabase-backed second brain. No data leaves your machine unless you configure it to.

**Web** (`compass_web.py`) — A stateless Flask app. No data is stored server-side. Each session lives only in your browser. Deploy it on your own VPS, share it with people you trust, and let them run their own sessions. Every person configures their own context, their own tracks, their own saboteur signatures. The synthesis is personalized every time.

---

## Setup

### Prerequisites

- Python 3.11+
- Anthropic API key (Claude Opus — CLI)
- OpenAI API key (web interface)

### Install

```bash
git clone https://github.com/cousingary/compass
cd compass
pip install -r requirements.txt
cp .env.example .env
# edit .env
```

### First run

```bash
python compass.py --setup
```

The setup wizard takes about five minutes. It captures your context, your primary tracks, your time horizon, your known saboteur signatures, and your preferred synthesis tone. This profile shapes every future synthesis. You can update it anytime by editing `~/.compass_config.json`.

### Run a session

```bash
python compass.py                    # bi-weekly
python compass.py --mode quarterly   # quarterly audit
python compass.py --review           # review recent sessions
```

### Web interface

```bash
python compass_web.py
# http://localhost:5050
```

For persistent deployment behind nginx, set `PORT` in your environment.

### Bi-weekly reminder

```cron
0 9 * * 4 [ $(( $(date +\%W) \% 2 )) -eq 1 ] && python /path/to/compass/compass_remind.py
```

Writes a flag to `~/.compass_due`. Check it however you prefer.

---

## Configuration

The CLI stores your profile at `~/.compass_config.json`:

```json
{
  "name": "Your name",
  "primary_context": "2-4 sentences. Who you are, what you're building, the core tension you're navigating.",
  "primary_tracks": [
    "The specific direction you're building toward",
    "A second track if relevant"
  ],
  "time_horizon": "6 months",
  "saboteur_signatures": [
    "avoidance of highest-leverage work",
    "overengineering before validating"
  ],
  "psychological_phase": "optional — where you are, not how you feel",
  "synthesis_tone": "direct"
}
```

The `saboteur_signatures` field is the one most people underinvest in. These aren't character flaws or emotional states. They're specific behavioral patterns — the exact moves your internal critic makes when it wants to slow you down. The more precisely you name them, the more precisely the synthesis can track whether they showed up.

The `primary_context` field is the one that changes most over time. Update it when your situation changes. The synthesis reads from it on every session.

The web interface takes the same fields as a form on each visit — no persistent server-side config, full personalization per session.

---

## Second Brain Integration

The CLI optionally ingests sessions into a Supabase-backed second brain. It attempts to import `log_pipeline_output` from `~/second-brain/ingest.py`. If the module isn't found, it skips silently.

When ingestion is active, sessions are stored as memories in the `personal_development` project (configurable) with full metadata: session type, date, non-negotiable, synthesis. This makes session history searchable and linkable to other memories — projects, decisions, insights — in the brain.

---

## The Deeper Use

The four questions aren't arbitrary. They're designed to cut through the narrative you tell yourself about your own productivity and surface what's actually happening.

Most people know, at some level, what their saboteur looks like. They've felt its effects for years. They've never named it precisely enough to track it.

The act of naming it — in a specific, behavioral form, every two weeks, in writing — does something different than journaling about it. It makes it auditable. The synthesis reads it against the context of what you said you were building. It looks for whether the same pattern is recurring. Over enough sessions, you start to see the shape of the thing.

That's the practice.

The AI doesn't fix anything. It reflects. You do the work.

---

## Example Config

```json
{
  "name": "J",
  "primary_context": "Building an AI-native content and intelligence infrastructure. Currently managing 3 active revenue streams while building toward a consolidated system that runs mostly autonomously. Core tension: breadth of vision vs. depth of execution.",
  "primary_tracks": [
    "Ship the autonomous content pipeline before end of Q2",
    "Reduce time spent on operations that don't compound"
  ],
  "time_horizon": "6 months",
  "saboteur_signatures": [
    "research loops that substitute for shipping",
    "optimizing systems that are good enough",
    "context-switching to low-stakes problems when the real work feels uncertain"
  ],
  "psychological_phase": "consolidation — closing loops, not opening new ones",
  "synthesis_tone": "direct",
  "optional_signal_field": true
}
```

---

## Example Session

```
══════════════════════════════════════════════════════════
  THE COMPASS — Bi-Weekly Session
══════════════════════════════════════════════════════════

  Thursday, March 25, 2026
  Session type: Bi-Weekly Calibration

────────────────────────────────────────────────────────
  1 / 4  —  EVIDENCE LOG
────────────────────────────────────────────────────────

  What did you build, ship, or complete in the past two weeks
  that didn't exist before? Verifiable outputs only.
  Not learning, not planning, not starting. Finishes.

  > Shipped the ingest pipeline for YouTube + podcast channels.
    Fixed three production bugs in the morning brief cron.
    Published two articles on the Tarotsmith site.

────────────────────────────────────────────────────────
  2 / 4  —  DRIFT AUDIT
────────────────────────────────────────────────────────

  Where did you spend time that wasn't consistent with your
  primary track? What was the real reason?

  > Spent about 6 hours across the two weeks researching
    podcast distribution platforms. The pipeline wasn't
    ready to distribute yet. Real reason: the next step
    (NotebookLM audio generation) felt uncertain and I
    substituted research for the thing I didn't know how to do.

────────────────────────────────────────────────────────
  3 / 4  —  SABOTEUR SIGNATURE
────────────────────────────────────────────────────────

  Did the internal critic show up in the past two weeks?
  In what specific behavioral form?

  > Yes. Research loop. When the NotebookLM API wasn't
    working on the first try, I spent two hours reading
    documentation instead of just reading the source code.
    Same pattern as last cycle, different surface.

────────────────────────────────────────────────────────
  4 / 4  —  NEXT FORTNIGHT'S NON-NEGOTIABLE
────────────────────────────────────────────────────────

  One specific output that will exist two weeks from now
  that doesn't exist today. Not a task. An artifact.

  > A working RSS feed at tubecap.mydomain.com with at
    least one published episode.

··········································································
  SYNTHESIZING
··········································································

══════════════════════════════════════════════════════════
  COMPASS SYNTHESIS
══════════════════════════════════════════════════════════

The pipeline shipped. That's real. Three production fixes
and two articles on top of new infrastructure is solid
evidence of movement.

The drift pattern is worth watching: research-as-avoidance
has appeared in two consecutive cycles now, both times
triggered by API uncertainty rather than genuine knowledge
gaps. This isn't a curiosity reflex — it's a delay
mechanism. The tell is that the research never resolved
the uncertainty; shipping did.

The non-negotiable is specific. An RSS feed with a live
episode is auditable. That's correct.

The question to carry: when the next API integration
breaks, what's the decision rule for when to read the
docs versus when to read the source?

*Two weeks of shipping things that break on contact with
reality.*
```

---

*Part of a personal AI infrastructure stack. Built for people who are serious about the gap between who they are and who they intend to be.*
