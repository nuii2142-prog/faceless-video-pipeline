# Upload kit — "Why Young People Don't Want to Farm Anymore"

Paste-ready metadata for YouTube Studio. Video: `final.mp4` (1920×1080, 2:43). Subtitles: upload `why-young-people-dont-want-to-farm-long.srt` separately (Subtitles → Add → Upload file → English, "with timing").

## Title
```
Why Young People Don't Want to Farm Anymore
```
Alt (A/B later): `Everyone My Age Left the Farm. I Stayed.`

## Description
```
The average farmer in America is now 58 years old. In Thailand, where I grew up, the story is the same — the land is aging and the young people are gone. This is the real reason an entire generation walked away from the soil… and why I chose to stay.

I'm a self-taught organic farmer in rural Thailand, teaching myself to build with AI from the same fields I wake up to before sunrise. This is a quiet look at why farming lost a generation — economics, status, and the things we forgot to measure — and why the future might grow from exactly the place everyone abandoned.

If this resonated, subscribe. I share slow thoughts on simple living, meaningful work, and finding the future in unexpected places.

📊 Source: USDA 2022 Census of Agriculture (NASS, 2024) — average U.S. farm producer age 58.1; over 40% of producers are 65+.

#simpleliving #farming #meaningfulwork
```

## Tags
```
why young people dont want to farm, farmer shortage, aging farmers, future of farming, simple living, organic farming, farming in thailand, leaving the farm, meaningful work, self improvement, slow living, agriculture crisis, ai in farming, sustainable farming, why farmers are quitting, rural life, finding purpose, farm to table
```

## Settings
- Category: **Education** · Language: **English** · ❌ Not made for kids
- Subtitles: upload the `.srt` (English)
- Pinned comment: `Would you ever go back to farming? Why or why not?`
- End screen: Subscribe + (next video when available)
- Playlist: create "Simple Living" / "Soil & Signal essays"

## ⚠️ Music note
`final.mp4` has "Way Back Home" mixed at 12%. If YouTube flags a Content-ID claim (or the track has vocals that clash with the narration), swap to a YouTube Audio Library instrumental and re-mix:
```
python scripts/assemble_clip.py why-young-people-dont-want-to-farm-long --landscape --music "SFX\<new-track>.mp3"
```

## Thumbnail
Base: `output/why-young-people-dont-want-to-farm-long/frames/...` or generate via `thumbnail_prompt.txt` (z-turbo) → add bold text in Canva: **WHY THEY ALL LEFT** (+ red underline). Keep ≤4 words, big, readable on mobile.
