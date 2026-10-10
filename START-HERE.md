# START HERE — Harshavi & Rishi

This folder is your project's "brain". Claude Code reads it so it knows the hackathon, the rules,
who does what, and how to explain things to you. You don't need to read every file — this page is enough to begin.

## What's inside
| Path | What it is |
|---|---|
| `CLAUDE.md` | Main briefing Claude Code reads automatically every time |
| `backend/CLAUDE.md`, `frontend/CLAUDE.md` | Extra briefing for Rishi's and Harshavi's halves |
| `.claude/agents/` | 10 specialist helpers ("subagents"), each set to the right model |
| `contracts/api-contract.md` | **The agreement between backend and frontend** — read this one together |
| `contracts/mock-predict-response.json` | Fake prediction so Harshavi can build before Rishi's API is ready |
| `docs/track-a-problem-statement.md` | The full problem statement |
| `docs/rules-and-gotchas.md` | Rules + common mistakes that lose points |
| `docs/timeline.md` | Day-by-day plan until Oct 14, 8 PM |
| `docs/submission-checklist.md` | Tick everything before submitting |
| `docs/decisions.md`, `docs/status.md` | Shared log of decisions + who's doing what |
| `docs/original-pdfs/` | The original problem statement PDFs |

## The subagents (helpers)
| Agent | Model | Use it for | Mainly |
|---|---|---|---|
| `ideator` | Opus | Turning the problem into 2–3 winning ideas | Both, first |
| `researcher` | Haiku | Quick lookups (docs, licenses) | Both |
| `ml-engineer` | Opus | Data, models, metrics, SHAP | Rishi |
| `api-builder` | Sonnet | FastAPI endpoints | Rishi |
| `heart-3d-engineer` | Sonnet | 3D heart + vessels | Harshavi |
| `dashboard-builder` | Sonnet | Form, risk cards, charts, disclaimer | Harshavi |
| `integration-tester` | Sonnet | Connecting both halves, end-to-end checks | Both |
| `rules-checker` | Opus | Audit against rules before submitting (read-only) | Both |
| `docs-writer` | Sonnet | README, 6-page report, video script, Devpost text | Both |
| `code-explainer` | Sonnet | "Explain this so I can answer a judge" (read-only) | Both |

**Opus** = strongest thinking (ideas, ML, audits). **Sonnet** = main builder. **Haiku** = fast and cheap for lookups.

## Step 1 — Install (each of you, once)
1. **Git**: https://git-scm.com/download/win (keep default options)
2. **Claude Code**: follow https://docs.claude.com/en/docs/claude-code/overview (Windows instructions)
3. Harshavi: **Node.js LTS** — https://nodejs.org · Rishi: **Python 3.11** — https://www.python.org (tick "Add to PATH")

## Step 2 — Open the project
1. Unzip this folder somewhere simple, e.g. `C:\hackathon\multimodal-ai-hackathon-2026`.
2. Open **PowerShell**, then:
   ```powershell
   cd C:\hackathon\multimodal-ai-hackathon-2026
   claude
   ```
3. Ask: "Which project subagents do you have, and what model does each use?" — it should list the 10 below.
   (Claude Code may ask you to **trust this folder** the first time — say yes; that lets it load the agents.)

## Step 3 — First prompts (copy-paste)
**Together, first (≈30 min):**
> Use the ideator agent to read the problem statement and propose 2–3 directions for our Track A project. Explain them simply.

**Then put it on GitHub (once, Harshavi):**
> Help me put this folder on GitHub as a public repo and add Rishi as a collaborator. I've never used git — explain every step before running it.

**Rishi:**
> I've put the dataset in backend/data/raw. Use the ml-engineer agent to inspect it and explain what's inside before writing any model code.

**Harshavi:**
> Use the heart-3d-engineer agent to set up the React app in frontend/ and show a rotatable heart with LAD, LCX, RCA colored from the mock data. Go step by step and explain what each thing is.

**Anytime:**
> Use the code-explainer agent to explain backend/src/train.py so I could answer a judge's questions about it.

**Before submitting:**
> Use the rules-checker agent to audit the whole project against the problem statement and the submission checklist.

## Working as two people
- Rishi works in `backend/`, Harshavi in `frontend/` — you rarely touch the same files.
- Push your work to GitHub at least twice a day; pull before you start.
- If you need to change the API, **talk first**, then update `contracts/api-contract.md` and `docs/decisions.md`.
- Update `docs/status.md` (or ask Claude to) when you finish something.

## Remember
- The rules allow Claude Code, but you **must disclose it** and **be able to explain your code**.
- Feature freeze **Wed Oct 14, 10 AM**. Submit by **8 PM**.
