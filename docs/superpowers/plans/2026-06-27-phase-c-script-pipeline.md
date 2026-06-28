# Phase C: Script Pipeline — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a `/faceless-short` Claude Code skill that accepts a topic or Thai notes file and outputs a HEIGHT-framework English script as `output/<slug>/script.json` + `output/<slug>/script.txt`, ready for Phase D (Chatterbox TTS).

**Architecture:** Three files — `SKILL.md` (Claude reads this when invoked, does the generation), `notes/_template.md` (raw content template), and `scripts/validate_script.py` (confirms output structure). No new Python packages needed — stdlib only.

**Tech Stack:** Claude Code skill (markdown), Python 3.14 stdlib for validator.

---

## File Map

```
C:\Users\Darks\.claude\skills\faceless-short\
  SKILL.md                          ← Claude Code skill — created in Task 3

C:\Users\Darks\Documents\2026 YT Short Project\
  scripts\
    validate_script.py              ← output validator — created in Task 1
  notes\
    _template.md                    ← Thai notes template — created in Task 2
  output\
    <slug>\                         ← created at runtime by the skill
      script.json
      script.txt
```

---

## Task 1: Write the output validator

**Files:**
- Create: `scripts\validate_script.py`

- [ ] **Step 1: Write `scripts\validate_script.py`**

```python
"""Validate script.json output from /faceless-short skill."""
import sys, json, pathlib

REQUIRED = ["slug", "topic", "hook", "explain", "illustrate", "teach",
            "narration", "word_count", "est_duration_sec"]

def validate(json_path):
    path = pathlib.Path(json_path)
    if not path.exists():
        return [f"file not found: {json_path}"]
    data = json.loads(path.read_text(encoding="utf-8"))
    errors = []
    for field in REQUIRED:
        if field not in data:
            errors.append(f"missing field: {field}")
        elif isinstance(data[field], str) and not data[field].strip():
            errors.append(f"empty string: {field}")
    wc = data.get("word_count", 0)
    if isinstance(wc, (int, float)) and wc < 80:
        errors.append(f"word_count={wc} below 80 (too short)")
    if isinstance(wc, (int, float)) and wc > 140:
        errors.append(f"word_count={wc} exceeds 140 (TTS > 60s)")
    txt = path.parent / "script.txt"
    if not txt.exists():
        errors.append("script.txt missing alongside script.json")
    return errors

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts\\validate_script.py output\\<slug>\\script.json")
        sys.exit(1)
    errors = validate(sys.argv[1])
    if errors:
        print("FAIL")
        for e in errors:
            print(f"  x {e}")
        sys.exit(1)
    print(f"OK — {sys.argv[1]}")
```

- [ ] **Step 2: Create a bad test file to confirm validator catches errors**

```powershell
New-Item -ItemType Directory -Force "output\_test_bad" | Out-Null
'{"slug": "test", "hook": ""}' | Out-File -Encoding utf8 "output\_test_bad\script.json"
```

- [ ] **Step 3: Run validator on the bad file — expect FAIL**

```powershell
python scripts\validate_script.py output\_test_bad\script.json
```

Expected output:
```
FAIL
  x missing field: topic
  x empty string: hook
  x missing field: explain
  x missing field: illustrate
  x missing field: teach
  x missing field: narration
  x missing field: word_count
  x missing field: est_duration_sec
  x word_count=0 below 80 (too short)
  x script.txt missing alongside script.json
```

If output says OK instead of FAIL, the validator has a bug — re-check the `REQUIRED` list and the empty-string check.

- [ ] **Step 4: Remove the bad test file**

```powershell
Remove-Item -Recurse "output\_test_bad"
```

---

## Task 2: Write the notes template

**Files:**
- Create: `notes\_template.md`

- [ ] **Step 1: Create `notes\` directory and write `_template.md`**

```powershell
New-Item -ItemType Directory -Force "notes" | Out-Null
```

Write `notes\_template.md`:

```markdown
# Notes: [Topic — Thai or English]
Date: YYYY-MM-DD

## เหตุการณ์ที่เกิดขึ้น / What happened
[เขียนภาษาไทยได้เลยครับ — describe the scene or experience]

## ความรู้สึก / How it felt

## สิ่งที่น่าแปลกใจ / The surprising or contrarian part
[อะไรที่คนอื่นมักจะคิดตรงข้าม / what most people assume that turns out to be wrong]

## สิ่งที่อยากบอกคนอื่น / The one thing to share
[ถ้าต้องบอกคนอื่นประโยคเดียว / if you had to say it in one sentence]
```

---

## Task 3: Write the skill (main deliverable)

**Files:**
- Create: `C:\Users\Darks\.claude\skills\faceless-short\SKILL.md`

- [ ] **Step 1: Create the skills directory**

```powershell
New-Item -ItemType Directory -Force "C:\Users\Darks\.claude\skills\faceless-short" | Out-Null
```

- [ ] **Step 2: Write `C:\Users\Darks\.claude\skills\faceless-short\SKILL.md`**

```markdown
# faceless-short — YouTube Shorts Script Generator

Turn a topic or Thai notes into a HEIGHT-framework English script for a faceless stickman-style YouTube Short.

## Invoke

```
/faceless-short "topic or Thai notes here"
/faceless-short notes/today.md
```

**Working directory:** Always run from `C:\Users\Darks\Documents\2026 YT Short Project\`

---

## Steps

### 1. Read input

If the argument ends in `.md`, read that file. Otherwise treat the argument as the topic directly. Thai text is fine — Gemini and Claude both read it natively.

### 2. Generate the HEIGHT script

Write a 4-beat script using this persona and rules.

**Persona (first-person — this is Nuay, not a character):**

Nuay (นุย) is a Thai organic farmer who wakes before sunrise to tend vegetables with his parents on their organic farm (ผักประสานใจ), a daily vipassana meditator (sampajañña — continuous clear awareness), and a self-taught AI/coding learner in rural Thailand.

**Audience:** English-speaking "simple living / self-improvement" — US, Australia, UK.

**The 4 beats:**

| Beat | What to write | Length |
|------|--------------|--------|
| **Hook** | One contrarian or surprising statement. Concrete and specific — NOT "I learned something unexpected." Example: "I used to think waking up early was discipline. Turns out it was just fear." Must stop scroll in 3 seconds. | 1–2 sentences |
| **Explain** | Unpack the hook. Why is this true? What's the insight behind it? | 2–3 sentences |
| **Illustrate** | One sensory, specific scene from Nuay's real life — farm, meditation, or coding. Use smell, sight, or sound. Make it feel real, not abstract. | 2–3 sentences |
| **Teach** | One simple, actionable takeaway. Calm energy — not preachy, not hype. | 1–2 sentences |

**Language rules (critical — this script will be read aloud by TTS):**
- Short sentences only. No long compound clauses.
- No emojis, hashtags, beat labels ("Hook:", "Explain:"), or stage directions.
- Clean spoken English. Conversational, not formal.
- Target: 90–120 words total.

### 3. Check word count before displaying

Count words in the full narration (all 4 beats joined).

- word_count < 80 → print: `⚠️ Script is short (N words) — hook may feel weak. Regenerate or continue?`
- word_count > 140 → print: `⚠️ Script is long (N words) — TTS will run over 60s. Trim or continue?`

### 4. Display the script

```
HOOK:
[hook text]

EXPLAIN:
[explain text]

ILLUSTRATE:
[illustrate text]

TEACH:
[teach text]

─────────────────────────────
NARRATION (for TTS):
[all 4 beats joined into one clean paragraph — no labels, no extra blank lines]

Word count: N | Est. duration: Ns
─────────────────────────────
```

est_duration_sec = round(word_count / 2.5)  ← TTS pace ≈ 150 WPM

### 5. Ask for confirmation

Print exactly:

```
Save this script? [y = save / n = discard / e = I'll edit first]
```

Wait for user response:

- **y** → go to Step 6
- **n** → print `Discarded.` and stop
- **e** → print `Paste your edited narration and I'll recalculate and save.` — wait, then save the edited version

### 6. Save output files

Derive slug: lowercase topic, spaces → hyphens, remove punctuation.
Examples: "Waking up at 5am" → `waking-up-at-5am` | "ปลูกผัก" → `pluk-phak`

Create `output/<slug>/` if it doesn't exist.

Write `output/<slug>/script.json`:
```json
{
  "slug": "<slug>",
  "topic": "<original topic string or filename>",
  "hook": "<hook text>",
  "explain": "<explain text>",
  "illustrate": "<illustrate text>",
  "teach": "<teach text>",
  "narration": "<hook + ' ' + explain + ' ' + illustrate + ' ' + teach>",
  "word_count": <integer count of words in narration>,
  "est_duration_sec": <round(word_count / 2.5)>
}
```

Write `output/<slug>/script.txt`:
```
<narration text only — no JSON, no labels, no extra whitespace>
```

### 7. Report

```
✅ Saved:
   output/<slug>/script.json
   output/<slug>/script.txt

script.txt is ready for Phase D (voice TTS).
Validate: python scripts\validate_script.py output\<slug>\script.json
```

---

## Notes Template

Raw notes go in `notes/` — copy `notes/_template.md` for each new clip and fill in Thai or English.
```

---

## Task 4: Smoke test

- [ ] **Step 1: Invoke the skill with a test topic**

In Claude Code, type:
```
/faceless-short "waking up at 5am to water the vegetables"
```

Expected: Claude displays the HEIGHT script with all 4 beats, then the narration block, then asks:
```
Save this script? [y = save / n = discard / e = I'll edit first]
```

If Claude doesn't recognise the skill, check that `C:\Users\Darks\.claude\skills\faceless-short\SKILL.md` exists.

- [ ] **Step 2: Save and confirm file creation**

Type `y`.

Expected:
```
✅ Saved:
   output/waking-up-at-5am/script.json
   output/waking-up-at-5am/script.txt
...
```

Confirm files exist:
```powershell
Get-ChildItem output\waking-up-at-5am\
```

Expected:
```
script.json
script.txt
```

- [ ] **Step 3: Run validator — expect OK**

```powershell
python scripts\validate_script.py output\waking-up-at-5am\script.json
```

Expected:
```
OK — output\waking-up-at-5am\script.json
```

If FAIL: read the error message, identify which beat/field is missing or empty, fix the wording in SKILL.md Task 3 Step 2 for that beat, re-run the skill.

- [ ] **Step 4: Read script.txt aloud (TTS sanity check)**

```powershell
Get-Content output\waking-up-at-5am\script.txt
```

Read it out loud. Check:
- No beat labels ("Hook:", etc.) in the text?
- All short sentences — no long compound clauses?
- Sounds like Nuay talking to a friend?
- Feels calm and authentic, not motivational-speaker hype?

If anything feels off, note it. You can refine the SKILL.md persona instructions and re-run.

---

## Task 5: (Optional) Initialize git

This project directory isn't a git repo yet. To start tracking:

```powershell
git init
@"
ml-env/
output/
__pycache__/
"@ | Out-File -Encoding utf8 .gitignore
git add scripts\validate_script.py notes\_template.md docs\ .gitignore
git commit -m "feat: phase-c validator, notes template, and spec"
```

Note: `C:\Users\Darks\.claude\skills\faceless-short\SKILL.md` lives outside this repo — back it up manually or track it in a separate dotfiles repo.
