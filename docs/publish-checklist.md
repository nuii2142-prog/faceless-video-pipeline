# Publish Checklist — รันก่อนกดเผยแพร่ทุกครั้ง

ให้ Claude ไล่เช็กทีละข้อกับ ep ที่จะลง แล้วรายงานว่าข้อไหนยังขาด:

```
[ ] ภาพทุก scene สไตล์ตรงกัน (เทียบ docs/visual-style.md + contact sheet)
[ ] Export ถูก ratio: 16:9 1080p (long-form) / 9:16 (Shorts)
[ ] Audio levels ok — เสียงพูดชัด, เพลง (ถ้ามี) ไม่กลบ, ผ่าน clean_voice.py แล้ว
[ ] Loudness ≈ -14 LUFS (assemble_clip.py ใส่ loudnorm อัตโนมัติแล้ว — เช็คได้:
    ffmpeg -i final.mp4 -af loudnorm=print_format=summary -f null NUL → ดู Input Integrated)
[ ] .srt sidecar พร้อม (ไม่ burn-in) + corrections.json แก้คำ Whisper ฟังผิดครบ
[ ] ทุก scene มีภาพ ไม่มีจอว่าง/เฟรมค้างผิดจังหวะ (ดู final.mp4 จริงอย่างน้อย 1 รอบ)
[ ] Title / description / tags ครบ (EN) — ไม่ clickbait
[ ] Thumbnail อัปแล้ว สไตล์ตรงกับคลิป (flux2), อ่านออกบนมือถือ, ข้อความ ≤ 5 คำ
[ ] เพลงมาจาก YouTube Audio Library เท่านั้น (กัน Content-ID) + เช็ก attribution
[ ] ถ้าใช้เสียง TTS/F5 → ติ๊ก altered-content disclosure ตอนอัปโหลด
[ ] End screen / subscribe
[ ] Nuay นอนพอ + ไม่ได้เร่งแบบฟุ้ง → ถ้าไม่ชัวร์ เลื่อนลงพรุ่งนี้
```

ที่มา: ปรับจาก SOP ใน Road data (SoilAndSignal) ให้ตรงกับ pipeline จริงของ repo นี้
