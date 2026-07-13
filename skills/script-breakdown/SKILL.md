# script-breakdown — Viral-format script writer + (post-audio) per-beat breakdown

Turn a topic (or Thai notes from Nuay's real life) into ONE flowing English narration in the
reverse-engineered **Zen format**, shaped by **HEIGHT as a whole-clip arc** (not rigid chunks).

> ⚠️ **WORKFLOW IS TWO PHASES, SPLIT BY THE AUDIO.** The scene breakdown does **NOT** happen while
> writing the script. It happens **AFTER** Nuay records the voice, driven by the **real Whisper
> timestamps** — because the only correct phrase boundaries are the ones the audio actually speaks.
> Pre-guessing scenes at script time and force-aligning them to audio later is WRONG (it drifts).

```
PHASE A  (this skill, first run)         PHASE B  (after Nuay returns audio)
─────────────────────────────────       ─────────────────────────────────────
topic → INTERVIEW Nuay → research         audio → Whisper timestamps (phrases = captions)
      → write narration
      → save script.txt/json                   → group phrases into VISUAL BEATS
      → STOP. hand off to Nuay.                → 1 meaning-first image prompt per BEAT
        (he records the voice)                 → human check → ComfyUI batch → contact sheet → assemble
```

> 🎯 North star = **long-form** (~8 min — the format that earns watch-hours / money). Short form is
> the validation step. Both via `--length`.

## Model guidance (READ FIRST)
- **PHASE A — narration writing = use Opus.** It is the creative core (emotion, rhythm, the Zen
  hook). Sonnet is not reliable enough here. Do not write the script on Sonnet.
- **PHASE B — run Whisper, group beats, write image prompts, drive ComfyUI = use Sonnet** to save
  Pro/Opus quota. B2/B3 involve real judgment but follow a clear method; Sonnet handles it.

## Invoke
```
/script-breakdown "topic or Thai notes"
/script-breakdown notes/today.md

Options (append after the topic):
  --length  short | long      default short (~90s, 1 pillar). long = ~8 min, 3 pillars.
  --research none | light | deep
        default light. none = experience only; light = 1 real stat; deep = 2-3 real stats.
        If --length long and --research is not given, default to deep.
```
Working directory: `C:\Users\Darks\Documents\2026 YT Short Project\`
(Reusing this skill on another machine/channel: swap the persona in A2 for your own real life and
adjust the working directory — everything else is portable.)

---

# PHASE A — Write the narration, then STOP

## A1 — Read input & options
- If the argument ends in `.md`, Read it (Thai is fine). Otherwise treat the string as the topic.
- Parse `--length` (default `short`) and `--research` (default `light`; `deep` if length=long and unset).

## A1b — INTERVIEW Nuay (ALWAYS, before research or writing — any topic)
The script's moat is Nuay's real life; an interview is how it gets into the script instead of
generic filler. Ask ONE compact message (Thai, numbered, answerable in fragments), tuned to the
topic — these five slots, skip any that the input already answered:

1. **เรื่องจริงของพี่** — ประสบการณ์ตรง/โมเมนต์จริงกับหัวข้อนี้? (ขอ 1 ภาพที่เห็น/ได้ยิน/รู้สึกจริง เช่น
   "เช้านั้นฝนเพิ่งหยุด มือยังเปื้อนดิน")
2. **ข้อมูลที่พี่มี** — ตัวเลข/ข้อเท็จจริง/แหล่งที่พี่มีอยู่แล้วอยากใส่ไหม?
3. **ให้ผมวิจัยไหม** — none / light (1 สถิติ) / deep (2-3 สถิติ)? (ถ้าไม่ตอบ ใช้ค่าจาก `--research`)
4. **คนดูควรได้อะไรกลับไป** — ความรู้สึก/ข้อคิดเดียวที่อยากให้ติดตัวไป?
5. **ภาพ/สถานที่จริง** — มุมไหนของไร่/ชีวิตจริงที่อยากให้ปรากฏ? (ผูกกับ `farm view Ref/` ถ้ามี)

Rules:
- Nuay answers กระชับได้ ("ข้าม" = ใช้วิจารณญาณของโมเดล) — never block on a skipped slot.
- ถ้า Nuay สั่ง "วิจัยให้เลย" ในคำตอบ → treat as research directive for A3.
- **Topic-agnostic:** the 5 slots work for farm, mindfulness, coding, or any future topic — only the
  wording of the examples adapts. For non-farm topics, slot 5 becomes "ภาพจริงจากชีวิตช่วงนั้น".
- Save the answers verbatim (Thai OK) into `script.json` → `"interview": {...}` (A8). The lived
  scene in A4 MUST come from slot 1/5 material when given — never invent a scene Nuay didn't live.

## A2 — Load references
- Read `docs/format-spec.md` — the Zen format (hook 4-beats / 3 pillars / transitions / authority / close).
- **Persona (first person — this IS Nuay, not a character):** wakes before sunrise to tend vegetables
  with his parents on their organic farm (ผักประสานใจ) in rural Thailand; practices daily vipassana
  (sampajañña — continuous clear awareness); teaching himself AI/coding from scratch. Audience:
  English-speaking "simple living / self-improvement" (US, UK, Australia).

## A3 — Research REAL evidence (amount = `--research`)
- `none` → skip. `light` → 1 genuine stat/study. `deep` → 2-3 (for long-form, ~1 per pillar).
- Each anchor needs: source/researcher + year + institution or journal + a specific number.
- ⚠️ **REAL ONLY.** Use web search and verify. NEVER invent a study, number, or name. If nothing
  solid is found, tell Nuay and offer to write it experience-only.

## A4 — Write ONE flowing narration (HEIGHT arc × Zen mechanics)
Continuous spoken English — NO beat labels, NO stage directions, NO scene numbers in the text.
HEIGHT is the emotional arc of the WHOLE piece, blended with `format-spec.md`:

**short (≤60s HARD CAP — aim 40-55s):** the 2026 Shorts algorithm ranks by absolute watch time
(swipe rate retired); sub-15s clips collapsed, 30-45s is the platform sweet spot, and Nuay caps at
60s. Retention target ≈70%+. Structure = Hook → 1 authority stat → ONE sensory scene from Nuay's
real life → quiet takeaway + **callback to the opening image** — but rotate the ORDER via the
structure wheel below.

> **⚙️ VARIATION WHEELS (Shorts — anti-repetition, 2026).** YouTube now runs an Anti-Repetitive
> Content AI: recycling the same hook/format/visual style across consecutive uploads gets
> suppressed. The DNA never changes (Zen voice · real cited stat · Nuay's real lived scene ·
> callback close · calm tone). What rotates is the surface. **Before writing, read the last 1-2
> `output/*/script.json` and pick variants that differ from the previous Short.**
>
> **Hook wheel (first ~5s — never repeat the previous Short's pick):**
> 1. `atmosphere` — immersive 2nd-person moment ("Tonight, when the sun goes down…")
> 2. `stat` — cold-open the strongest number, blunt ("97% of day traders lose money. I was one of them.")
> 3. `result` — show the END state first, then rewind ("This basket feeds twenty families. It started as a debt.")
> 4. `claim` — bold contrarian one-liner ("Weeding made me faster. Because it made me slower.")
> 5. `you` — direct address that names the viewer ("If you check your phone before your feet touch the floor…")
>
> **Structure wheel (body order — differ from the previous Short):**
> - `S1 classic` — hook → stat (authority) → lived scene → takeaway + callback
> - `S2 story-first` — hook → lived scene → the stat lands as the twist → takeaway + callback
> - `S3 question-loop` — hook opens a question → mini-scene → stat → the answer IS the callback
>
> Record both in `script.json` (`"hook_variant"`, `"structure_variant"`). Compare 10-second
> retention in Analytics; when a wheel position clearly wins, weight it more often — but never
> run the same combo twice in a row (the wheel exists for the algorithm, not for taste).

**long (~8 min):** Hook (4 beats) → **3 pillars** (each: transition sentence → real anchor → a
Nuay-life illustration → one memorable line) → close (reframe + 3-beat recap + callback).

> **Hook energy — compensate for a naturally low/monotone voice (2026-07-13, Nuay's note after
> watching `the-five-minute-commute`'s first 30s and finding it not compelling enough).** Nuay's
> voice is genuinely deep and calm — that IS the brand — but it means the writing has to carry
> more of the hook's pull than vocal tone alone can, or viewers drop before the payoff lands. Lean
> the overall script voice a little more playful/curious where it naturally fits (a wry aside, an
> unexpected juxtaposition, a small twist) — keep the calm register, just don't let it go flat.
> Two concrete hook fixes, grounded in `docs/format-spec.md`'s own reference video (7.7M views):
> - **Land a real number inside the hook itself, by ~0:20-0:30 — not just a question.** B3
>   ("raise stakes") pairs the open question with ONE vivid stat in the same breath in the
>   reference clip. `the-five-minute-commute`'s hook asked "what is that hour costing you?" but
>   held its 40% stat back until 1:26 — past the window that decides whether someone keeps
>   watching. Tease the sharpest number early even if its full study/context lands later in a pillar.
> - **The hook's visual beats (Phase B) must cut faster than the body.** No single beat in the
>   first ~30s should hold longer than ~3s — treat B2's "hook may cut faster" as a hard cap for a
>   script this calm, not a suggestion.
> Validate for real once a video is public: check YouTube Studio's 0:00-0:30 audience-retention
> curve. If a hook choice measurably holds more viewers past 0:30, weight it more next time.
>
> **Long-form variation (lighter touch — the 3-pillar engine IS the strength, keep it):**
> - Hook beat B1 opener imagery must differ from the previous long-form's B1 (check the last
>   long `script.json`); the hook wheel above can seed B1's flavor.
> - Transition sentences: never reuse the same bridge twice within one video, and don't open
>   two consecutive videos' pillars with the identical stock phrase — paraphrase in Zen voice.
> - Pillar order: when the material allows, vary which pillar type leads (history-first vs
>   science-first vs personal-first). Record `"structure_variant": "P-history|P-science|P-personal"`.

Personal experience = the heart; the researched stat(s) = the authority. Short declarative sentences,
second person where it fits, present tense, calm/awe-building, no emojis.

> **Foreign names & Pali terms:** each one you keep in the script ("teikei", "sampajañña", a
> researcher's name) is a near-guaranteed Whisper mishear later. Keep them — they carry authority —
> but keep the list short, and expect to fix them in B3's corrections step.

## A4b — Kill the AI tells (genre-tuned anti-slop)
A script that reads like ChatGPT is what gets a faceless channel dismissed as "AI slop"
and hurts both retention and monetization review. But the Zen format *wants* some
heightening — do not strip it flat. Cut the tells, keep the voice.

**REMOVE always:**
- **Em dashes (—).** They leak into the .srt captions. Use a period or "and".
- **Throat-clearing openers:** "Here's the number that…", "Here's the thing", "The truth is",
  "What's fascinating is". Cut straight to the fact.
- **Intensifiers / adverbs:** very, really, simply, truly, incredibly, just. Delete — let the
  noun and verb carry the weight ("hard to count" > "very hard to count").
- **Inanimate agency:** "the data tells us", "the decision emerges". Name who acts.

**USE SPARINGLY — max ONCE per script each (potent, but formulaic in bulk):**
- "Not X. It's Y." contrast.
- Negative listing ("Not a paycheck. Not on time.").
- Three-fragment staccato ("The land is aging. The children left. So who grows it?").
- A pull-quote closing line.

**KEEP — this is the Zen voice, not slop:**
- One rhetorical-question pivot per section.
- One anaphora triad for rhythm ("We told them… We told them… We never told them…").
- The closing callback to the opening image.

**Final check:** read the draft out loud. If a line sounds like a LinkedIn post, rewrite it
as something Nuay would actually say standing in a field at 5am.

## A5 — Length check
Count words. **short: warn if <90 or >140** (Nuay's slow VO ≈130 wpm ⇒ 140 words ≈ 60s hard cap;
aim 100-125 words = 45-55s). long: warn if <1000 or >1600.
est_duration_sec = round(words / 2.2) (calibrated to the ~130 wpm delivery, not fast TTS).
Show the warning and wait if triggered.
> Nuay may cap length for TTS-credit reasons — honor an explicit word target over these defaults.

## A6 — Display the NARRATION ONLY (no breakdown here)
```
NARRATION (read aloud / feed to TTS):
[full flowing narration]

Words: N | Est: ~Ns | Length: short/long | Research: level
Real source(s): <citation(s)>
```
> Do **NOT** print a numbered phrase/scene table in Phase A. Scenes come from the audio in Phase B.

## A7 — Confirm
`Save? [y / n / e = edit narration first]` — wait. On `e`, take the edited narration, recount (A5), save.

## A8 — Save to `output/<slug>/` (slug = lowercase topic, spaces→hyphens, punctuation removed)
- `script.txt` — clean narration only (for recording / TTS). No labels, no trailing whitespace.
- `script.json`:
```json
{
  "slug": "...", "topic": "...", "length_mode": "short|long", "research_level": "none|light|deep",
  "narration": "...",
  "sources": ["researcher, year, institution — the real stat"],
  "interview": { "story": "...", "own_data": "...", "research_wanted": "...", "takeaway": "...", "real_place": "..." },
  "hook_variant": "atmosphere|stat|result|claim|you",
  "structure_variant": "S1|S2|S3 (short) or P-history|P-science|P-personal (long)",
  "word_count": 0, "est_duration_sec": 0
}
```
> No `phrases` / `scene_count` here — those are NOT decided yet. They are produced in Phase B from
> the real audio. (A provisional split, if ever shown, is throwaway and never saved.)

## A9 — Hand off and STOP
```
✅ Saved: output/<slug>/script.txt, script.json
Next (you): record script.txt IN YOUR OWN VOICE (a calm, slow read — your accent is the brand,
not a flaw). Drop the .mp3/.wav into output/<slug>/, then tell me and I'll run Phase B.

VO direction (self-record):
  PACE: slow, unhurried (~130 wpm) — like speaking to one person at dusk
  PAUSES: full stop at every line break; let silence breathe
  HOOK: near-whisper · CLOSE: lift very slightly, hopeful but quiet
  RE-RECORD any line that sounds "announced", rushed, or salesy
  FORMAT: WAV, quiet room, keep raw takes — clean_voice.py handles noise/loudness after
> Why your real voice: it is the one asset no competitor can clone, the strongest authenticity
> signal for YouTube's anti-"inauthentic content" review, and it removes the synthetic-media
> disclosure question. Current alternative: ElevenLabs Professional Voice Clone of Nuay's own
> voice (trial 2026-07-11). F5-TTS (`scripts/f5_speak.py`, tuned 0.84/cfg 1.8/nfe 85) exists as
> an emergency fallback but Nuay judged its delivery too flat to publish. Any synthetic voice:
> tick YouTube's altered-content disclosure on upload.
```
Then **stop**. Do not run Whisper, do not invent scenes, do not generate images. If you have a genuinely
useful idea (a stronger hook, a better stat, a thumbnail/title angle), offer it briefly. Ask if anything
is unclear. Otherwise wait for Nuay's audio.

---

# PHASE B — After Nuay returns the audio: breakdown FROM the audio

> Trigger: an audio file exists in `output/<slug>/` and Nuay says to continue. Prefer **Sonnet** here.

## B1 — Whisper timestamps + phrase segmentation
Run (uses the project's `ml-env` Python, which has faster-whisper):
```
ml-env\Scripts\python.exe scripts\whisper_phrases.py "<audio path>" <slug>
```
This writes:
- `words.json` — every word with start/end (reference).
- `scenes.json` — phrases segmented from the audio itself (punctuation + real pauses), ~1.5-3s each.

**These phrases are CAPTION-sized, not image-sized.** They become the .srt cues as-is (short cues
read well). The image timeline is coarser — that's B2. Review the printed report: audio duration,
phrase count, no zero/negative durations.

## B2 — Group phrases into VISUAL BEATS
One image per ~2s phrase produced 220+ images per long clip — half of them 2-word fragments
("Yet,", "In 1986,") that can't carry a picture, so they got filled with meaningless icon cards,
and image generation + Ken Burns time doubled. A **beat** = one visual idea on screen.

Read `scenes.json` and group **consecutive** phrases into beats:
- **Target 3-6s per beat** (1-3 phrases). Hook may cut faster (~2-3s) to grab; the close may
  breathe (6-8s). Nothing over ~8s — a still held longer drags even with Ken Burns.
- Merge a fragment with the phrase that completes its thought ("Then at seven," + "I close the
  laptop…"). Never merge across a section turn (hook→pillar, pillar→pillar, →close).
- A strong phrase stands alone: a stat reveal, a punchline, the central question — give each its
  own beat even if short. Emphasis = a cut.
- Sanity: a 10-min clip should land around **100-140 beats** (~half the phrase count); a ≤60s
  Short around **14-22**.

## B3 — One image prompt per beat → `scene_prompts.json`
Read `docs/visual-style.md` (locked style) first. Then, before writing any prompt:

**Meaning comes from script.txt, timing from scenes.json.** Whisper mishears names and splits
sentences oddly ("Taike" for "teikei", "It is not in the early 1970s."). Writing a prompt from
garbled text gives a wrong image. Where a phrase looks off, find the real sentence in `script.txt`
and depict THAT. (Captions don't need a corrections file anymore — `make_srt.py` builds them by
aligning `script.txt` directly to large-v3 word timings, so the .srt text is always the true script.)

**Plan this video's visual language (5 lines, once).** List 3-5 recurring motifs from THIS story's
world (e.g. this clip: weed rows / the noon sun / the laptop at the wooden table / the alarm clock)
and 1-2 planned callbacks (the close should visually answer the open). Deliberate repetition of a
motif builds cohesion; accidental repetition of clip-art reads as laziness. Metaphors must come
from the story's own world, never from the generic icon shelf (lightbulb, handshake, target).

**Every beat's `visual` MUST name a SETTING + a CAMERA** from the menus in `docs/visual-style.md`
(location menu = Nuay's real farm, photographed in `farm view Ref/`). BASE_STYLE carries zero
scene content by design — if the visual doesn't say where we are and from what angle, the model
invents the same generic outdoor frame every time. The setting must MATCH the meaning: sleeping
happens INSIDE the wooden room (walls + floor visible), desk work at the under-house table or
indoors at night, field lines in the plowed beds / vegetable rows / paddy. Farm wide shots end in
low forested hills or a tree wall, never a city skyline (skylines belong only to city beats).
The farmer hat lives in CHARACTER_STYLE — don't restate it, but you MAY use it as a story prop
(hung on a peg = rest; lifted on = the day begins). A farm dog is welcome as a small life detail.
One amber-gold accent is reserved for sun / dawn glow — write stat numbers as "large deep
amber-gold NN%" in the stat beat itself, never elsewhere.

**Per beat, ask: "sound off, would a viewer FEEL this line from the image alone?"** Then pick the
device that shows it — whatever the content calls for, in any ratio. There are NO shot-type quotas:
- **Literal action** — someone does the thing. Default whenever the line has a doable verb.
- **Place / weather** — the environment carries the feeling (dawn field, brutal noon glare).
- **Emotion close-up** — the character's face/posture when the line is about an inner state.
- **Contrast / split-frame** — the line compares two things? Show both halves.
- **Progression** — change over time in one frame (seed → sprout → plant).
- **POV** — the line addresses "you"? Show the viewer's own hands/phone/desk.
- **Scale** — the line is about magnitude? Make the size difference the picture.
- **Stat card** — a clean number card ("58", "46.9%", simple pie) for every real statistic. The
  viewer must SEE the number for the authority beat to land. (z-turbo renders digits bold — fine.)
  Write the brand treatment INTO the beat's `visual`: "a large deep amber-gold number 97% floating
  in a calm open sky above a quiet field, nothing else". Never put a draw-the-number instruction in
  BASE_STYLE — it applies to every frame and cfg-1 will stamp a random gold digit on all of them
  (verified twice, 2026-07-09).
- **Symbol** — LAST resort, for purely abstract connectives only, and drawn from this video's
  motifs, not stock icons.
- **Playful object B-ROLL — aim for ~10-15% of beats.** Fun close-ups of story-world objects
  give the eye a rest from people-and-places and add rhythm: eggs in a woven basket, a drip
  line beading water, muddy boots by the door, a kettle steaming, a seedling tray, the dog's
  ear flicking. Concrete, charming, one object each.
- **Callback** — re-show an earlier frame, evolved. Strongest at the close.

Bad→good, from a real clip:
- "we grow for people we know by name" — ✗ a nametag icon beside a vegetable icon →
  ✓ the character writing a family's name on a small basket of vegetables.
- "A wandering mind is an unhappy mind" — ✗ a thought-bubble with a scribble →
  ✓ the character walking one way while a faint ghost-copy of them drifts the other way.
- "you and I will start the day with the same job" — ✗ two alarm-clock icons →
  ✓ split frame: the character waking on a farm mat, a generic figure waking in a city bed,
  the same stretching pose.

**Anti-icon-slop rules.** "a small X icon beside a tiny Y icon" is the visual em-dash — one is
fine, eighty are slop (a real clip hit 82/221). Never two icon-pair beats in a row; keep them
under ~1 in 10 overall. The nouns of a phrase are not its meaning — depict what the sentence
*does*, not the words it contains. If >50% of beats come out B-ROLL, you almost certainly
icon-slopped; revisit.

Schema (one object per beat; `scene` = the FIRST phrase it covers, so frames keep their names):
```json
[{ "scene": 12, "covers": [12, 13, 14], "phrase": "joined text of the covered phrases",
   "shot_type": "B-ROLL|CHARACTER|ATMOSPHERE", "visual": "..." }]
```
`covers` may be omitted for a 1-phrase beat. Every scenes.json phrase must be covered exactly once
(`assemble_clip.py` validates). `shot_type` still gates CHARACTER_STYLE injection — set it by what
the visual actually shows. Aspect: **9:16** Shorts / **16:9** long-form (`batch_zturbo.py --portrait`
flips both the latent and the style line; `assemble_clip.py --landscape` must agree).

## B3b — Self-review, then the human gate
Scan the finished list once, as a reviewer:
1. Same composition or same prop within any ~6-beat window (and it's not a planned callback)? Vary it.
2. Three+ consecutive beats with the same device or shot_type? Break the run.
3. Any beat that fails the sound-off test? Rewrite it — that one WILL read as "AI slop" on screen.
4. Icon-pairs over ~10%? Convert the weakest into literal action / place / character beats.
5. **Cross-clip opening check (anti-repetition, 2026):** read the PREVIOUS clip's
   `scene_prompts.json` first beat — this clip's opening visual must differ in at least two of
   {setting, camera, subject}. The algorithm's repetition detector sees the first frames of
   consecutive uploads; identical openers read as a template channel.
6. **Standing-wide budget: max 2 "character stands/walks in a field, full body, wide" beats per
   clip** (morning-before-the-sun-short shipped 5 — the whole back third looked identical at
   video speed). Consecutive CHARACTER beats must change at least TWO of {camera distance,
   angle, action/prop}: wide walking → close-up on hands in the soil → over-shoulder at the
   seedling → looking up at the sky. Emotional beats especially want CLOSE, not another wide.

Then show Nuay: beat count, shot-type mix, the planned motifs/callbacks, and the 5 beats you're
least confident about (phrase + visual). **Wait for his OK before generating** — images cost
~26s each on the 5070; a 2-minute check protects a ~1-hour GPU run.

## B4 — Breathing room (intro / outro) — automatic in assembly
These come from `assemble_clip.py`; do NOT time them in scenes.json:
- **Lead-in ~1s** — frame 1 holds before the voice starts (the viewer settles in).
- **Outro ~2.5s** — a final frame holds after the voice ends (let it land).
- **Fade** — the voice eases in/out; the video fades to black at the very end only (the lead-in
  hold does the settling at the start — there is no fade-from-black).
Optionally author ONE dedicated **outro visual** (a calm resolution image — e.g. the figure
looking at the horizon, lots of empty space) and save it as `frames/scene_end.png`; assembly
holds THAT through the outro instead of freezing the last narration frame. Tune per clip with
`--lead-in` / `--outro`.

## B5 — Voice → images → contact sheet → captions → assembly
**Voice (ElevenLabs PVC, current default, 2026-07-13): use the raw exported mp3s AS-IS.** Concat
the PVC takes straight to `voice.wav` (ffmpeg concat, no filters) — do NOT run `clean_voice.py` on
it. PVC audio is already studio-clean; running the denoise/highpass chain on it added a hollow/
"boomy" artifact (confirmed on `the-five-minute-commute`, rejected by Nuay). `clean_voice.py`
still applies to genuine self-recorded raw takes (real mic/room noise) per A9 — the distinction is
PVC vs a physical recording, not a blanket rule. `assemble_clip.py` already applies loudnorm to
-14 LUFS at mux time, so no separate loudness pass is needed either way. Do not reprocess the
voice unless Nuay asks.
```
ComfyUI open → python scripts\batch_zturbo.py <slug>              (add --portrait for 9:16; resumable, ETA shown)
check        → ml-env\Scripts\python.exe scripts\contact_sheet.py <slug>
                 ↳ Nuay eyeballs the grid; re-roll a bad frame:
                   delete frames\scene_NN.png → python scripts\batch_zturbo.py <slug> --only NN --seed 7
grade        → ml-env\Scripts\python.exe scripts\grade_frames.py <slug>   (AFTER the human gate — the
                 "Soil & Signal dawn" house grade + paper grain; writes frames_graded/. Re-run after
                 any re-roll. Every published frame goes through this.)
captions     → ml-env\Scripts\python.exe scripts\make_srt.py <slug>   (script-aligned to large-v3 WORD
                                                                   timings — accurate sync; sidecar .srt,
                                                                   do NOT burn in — upload in YouTube Studio)
assemble     → python scripts\assemble_clip.py <slug> --frames-dir frames_graded [--landscape] [--ken-burns]
```
`--ken-burns` renders scenes in parallel (`--jobs`, default ~6) — a long clip takes minutes, not
an hour. Run it in the background and report the printed ETA.

**Music: CHANNEL BLEND at 3% (2026-07-13, revised — supersedes the earlier "default NONE").**
Nuay generated a locked 5-track channel signature on ElevenLabs Music v2 (instrumental, guitar +
kalimba = "soil", faint synth sparkle = "signal"). They live in `Music/` at repo root (one canonical
file per role — regenerate via `Music/PROMPTS.md`, verify low-band % before replacing any of these):
- `Music/Hook.wav` — ~86 BPM, energetic (opens the video, first ~30-40s)
- `Music/Main Theme.wav` — ~76 BPM, calm bed/anchor — used for short-form AND long-form pillar 1
- `Music/Main C.wav` — brighter, kalimba-led — long-form pillar 2 (curious/creative content)
- `Music/Main D.wav` — warm pad, more reflective — long-form pillar 3 (closing/rumination content)
- `Music/Outro.wav` — the closing sign-off sting (the last ~10-12s)
All tuned so the low band (60-250 Hz) stays near Nuay's own voice (21-36% vs his 23%) — so they DON'T
muddy his deep voice. Verify any new channel track the same way (librosa low-band %) before shipping it.

**Short-form blend** (approved on `the-five-minute-commute-short`): Hook at **3%** for the first 30s
→ 3s crossfade → Main Theme bed at **3%** (self-crossfade loop to cover the length) → Main Theme fades
out ~7s before the end as Outro swells in at **~12%** (louder on purpose — it's the recognizable
button, and the voice has ended by then so nothing clashes). Whole mix re-loudnorm'd to -14 LUFS.

**Long-form blend** (~8:25 runtime, one Main variant per pillar so the bed never loops the same 60s
for minutes — map to `seo_youtube.md` chapters): Hook 3% (0:00-0:43) → Main Theme 3% (0:43-3:39,
pillar 1) → Main C 3% (3:39-5:24, pillar 2) → Main D 3% (5:24-8:17, pillar 3) → Outro ~12% (8:17-end).
4s crossfades at pillar boundaries.

`assemble_clip.py`'s single-track `--music` can't do a multi-part blend — mix it as a post step with
ffmpeg (extract the graded voice+fx from `final.mp4`, layer tracks on a canvas of the video's duration
with `adelay`/`afade`/`volume`, `amix ...:normalize=0`, then loudnorm), then mux onto the graded
`final.mp4` as `final_music.mp4`. Keep `final.mp4` as the clean voice-only master. If the long-form
frames are already graded, this is audio-only — no re-render needed for the music.
For a quick voice-only-plus-simple-bed case, `--music "Music\Main Theme.wav" --music-vol 0.03` still works.
⚠️ **ElevenLabs Music is NOT the YouTube Audio Library** — confirm the plan's commercial/monetization
license covers publishing, and that the tracks carry no Content-ID claim, before shipping on a monetized upload.

## B6 — Before upload
Run `docs/publish-checklist.md` against the ep and report what's missing. Do not skip the last
item (sleep guardrail) — late is better than scattered.

**Platform scope by length_mode (2026-07-13) — check `script.json` before writing any SEO copy:**
- **`length_mode: "long"` → YouTube only.** Write title/description/tags/chapters. Do NOT write
  Shorts/Facebook/IG Reel/TikTok copy for it — those belong to the short-form cutdown, a separate
  piece made later, not this upload.
- **`length_mode: "short"` → full multi-platform pass:** YouTube Shorts + Facebook + IG Reel +
  TikTok (+ a TikTok thumbnail prompt). If unsure which applies, ask rather than assume.

---

## Cost map per clip
- **Script writing** (Phase A): **Opus** — creative, worth the quota.
- **Voice (current plan, 2026-07-11):** **ElevenLabs Professional Voice Clone of Nuay's own
  voice** — Creator plan, batch-and-pause rhythm (~$8-11/mo effective; see memory
  project-budget-voice-strategy). Still synthetic ⇒ ALWAYS tick the altered-content disclosure.
  F5-TTS local (`scripts/f5_speak.py`, tuned 0.84/cfg 1.8/nfe 85, ref `voice over/voice 02.wav`
  + transcript) = free emergency fallback — Nuay judged it too flat to publish. Recording
  himself stays the zero-cost, zero-disclosure gold standard.
- **Timestamps + beats + image prompts + assembly** (Phase B): **Sonnet** + local tools — cheap/free.
- **Images:** local ComfyUI on the RTX 5070 (free). ~20-30 beats (short) ≈ 10-15 min;
  ~100-140 beats (long) ≈ 45-60 min at ~26s/img.
- **Ken Burns assembly:** ~2-5 min for a long clip (parallel), ~1 min for a Short.

---

## Monetization guardrails (keep the channel eligible)
YouTube de-monetizes faceless channels under its **"inauthentic / repetitious content"** policy,
not for using AI. This project's defense is real: a real person's life + real, cited stats. Protect it.
- **Voice = Nuay's likeness.** Current plan: ElevenLabs Professional Voice Clone of Nuay's OWN
  voice (see Cost map) — a real person's identifiable voice is the authenticity signal AND the
  hardest thing to copy. **Any clone is still synthetic audio: tick YouTube's altered-content
  disclosure on every upload** — the disclosure costs ~nothing; an undisclosed synthetic voice
  that gets flagged is the real monetization risk. (Recording himself for real removes the
  disclosure entirely.)
- **Music = cleared only.** Nuay's SFX/ folder is all YouTube Audio Library (cleared for monetized
  use) — that's the safe pool. The risk is grabbing a track from *outside* it (a random download,
  a "free" track that carries a Content-ID claim); that diverts ad revenue or blocks the video.
  Stay inside the Audio Library and check the track's license note (a few ask for attribution).
- **No mass-production look.** One genuine point of view per video. Never re-skin the same script with
  a new topic; vary the hook and structure. Quantity-farming is exactly what the policy targets.
- **Stats stay REAL and cited** (enforced in A3). One fabricated number that gets caught kills trust.
- **YPP bar to aim for:** 1,000 subscribers + 4,000 public watch-hours/12mo (long-form) OR 10M Shorts
  views/90 days. Long-form watch-hours are the realistic path here — which is why long-form is the north star.
