# Soil & Signal — channel music prompts (ElevenLabs Music v2)

Sonic identity: fingerpicked acoustic guitar + kalimba ("soil", handmade/organic) + a faint synth
sparkle ("signal"). Instrumental, calm, mindful, warm dawn feeling. **The load-bearing rule that
makes these sit under Nuay's deep voice: keep the LOW END empty** (no bass instrument, no kick) —
front-load that in every prompt because the auto-enhancer tends to add bass back if you don't repeat it.

## ElevenLabs settings (do this every time)
- **Vocals: OFF** (instrumental only).
- **BPM: lock it if the UI lets you** — ~76 for Main Theme, ~86 for Hook, ~80 for Outro. (Auto often
  drifts / the tempo detector reads double.)
- **Same key for all Main Theme variants if possible** (e.g. all in C or G major) so they cross-fade
  cleanly when rotated inside one long-form video.
- **Length ~60s** for Hook/Main Theme (assemble loops/trims to fit); ~12s for Outro.
- After generating, verify the low band with the librosa check (target 60-250 Hz ≈ Nuay's voice ~23%,
  not 40%+). If it comes back bass-heavy, regenerate — don't ship it.

## Long-form usage (~8 min)
Hook (first ~40s) → rotate a **different Main Theme variant per pillar** (~2 min each, 3 pillars) so
the bed never loops the same 60s for minutes → Outro on the close. That's why there are several Main
Theme variants below — generate 2-3 and assign one to each pillar.

---

## HOOK (energetic opener, ~86 BPM) — reuse `Hook.wav`, or regen with:
```
Instrumental, no vocals, 86 BPM. Warm acoustic-folk-electronic. Fingerpicked acoustic guitar motif
high on the neck, livelier light percussion (shaker, soft claps, rim taps — NO kick, NO bass drum),
playful kalimba accents, a bright plucked synth arpeggio in the upper register. CRITICAL — no bass
instrument of any kind, keep the low end empty and clean for a deep male narration voice. Mood:
energetic, warm, curious, motivated — the feeling of eagerly starting something. Seamless loop.
```

## MAIN THEME A — "balanced anchor" (~76 BPM) — this is `Main Theme.wav`, regen with:
```
Instrumental, no vocals, 76 BPM. Warm, calm, gently hopeful. Fingerpicked acoustic guitar plays a
simple repeating motif high on the neck, with kalimba and glockenspiel sparkles and a soft shaker
pulse; a faint warm synth pad glows underneath. Airy, open, spacious — sunrise on a dirt path.
CRITICAL — keep the low end almost empty: NO bass guitar, NO upright bass, NO synth bass, NO kick
drum. Everything light and mid-to-high so a deep male voice sits underneath. Seamless loop. Mood:
grounded, mindful, unhurried but alive.
```

## MAIN THEME B — "guitar-intimate" (sparser, reflective pillar, ~74 BPM)
```
Instrumental, no vocals, 74 BPM. Intimate and sparse. Just a fingerpicked acoustic guitar playing a
gentle repeating motif high on the neck, a few soft kalimba notes, and a lot of quiet space around
them — almost no other layers. CRITICAL — no bass of any kind, no drums, no kick; the low end stays
empty for a deep male narration voice. Warm, tender, close-mic feel. Seamless loop. Mood: calm,
personal, honest — like remembering something quietly.
```

## MAIN THEME C — "kalimba-bright" (curious/doing pillar, ~80 BPM)
```
Instrumental, no vocals, 80 BPM. Bright and gently moving. Kalimba and glockenspiel lead a playful
repeating motif, with fingerpicked acoustic guitar underneath and a light plucked synth arpeggio in
the upper register; soft shaker keeps a walking pulse (NO kick, NO bass drum). CRITICAL — no bass
instrument, no low end; keep the bottom of the mix open for a deep male voice. Seamless loop. Mood:
curious, warm, quietly upbeat — the feeling of figuring something out.
```

## MAIN THEME D — "warm-pad" (spacious closing pillar, ~74 BPM)
```
Instrumental, no vocals, 74 BPM. Soft and spacious, almost ambient. A warm analog synth pad glows
gently, with a slow fingerpicked acoustic guitar motif and occasional single kalimba notes drifting
over the top. CRITICAL — no bass instrument, no kick, no low end; everything sits in the mid and high
register so a deep male voice fills the bottom. Seamless loop. Mood: reflective, peaceful, resolved —
a slow exhale at the end.
```

## OUTRO (closing sign-off, ~80 BPM, ~12s) — reuse `Outro.wav`, or regen with:
```
Instrumental, no vocals, ~12 seconds, 80 BPM. A short warm closing signature using the same
fingerpicked acoustic guitar motif, resolving to one sustained kalimba note and a soft shaker fade.
Bright, mid-high, quietly satisfying. NO bass, NO drums, NO low end — light and airy only. A
recognizable channel sign-off.
```
