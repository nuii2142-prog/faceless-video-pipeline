# Publish Checklist — รันก่อนกดเผยแพร่ทุกครั้ง

ให้ Claude ไล่เช็กทีละข้อกับ ep ที่จะลง แล้วรายงานว่าข้อไหนยังขาด:

```
[ ] ภาพทุก scene สไตล์ตรงกัน (เทียบ docs/visual-style.md + contact sheet)
[ ] ทุกเฟรมผ่าน grade_frames.py แล้ว (house grade + grain) และ assemble ใช้ --frames-dir frames_graded
[ ] Export ถูก ratio: 16:9 1080p (long-form) / 9:16 (Shorts)
[ ] Audio levels ok — เสียงพูดชัด, เพลง channel blend **4%** base bed (Hook→Main Theme→Main C→Main D,
    ไม่กลบเสียงพูด) + outro ค้าง **~20% ช่วง 6 วิสุดท้าย** (มาตรฐานใหม่ 2026-07-18 — ดู SKILL.md B5),
    เสียง PVC ใช้ raw ไม่ผ่าน clean_voice.py
[ ] Loudness ≈ -14 LUFS (assemble_clip.py ใส่ loudnorm อัตโนมัติแล้ว — เช็คได้:
    ffmpeg -i final.mp4 -af loudnorm=print_format=summary -f null NUL → ดู Input Integrated)
[ ] .srt sidecar พร้อม (ไม่ burn-in) — `make_srt.py` align ตรงกับ script.txt อยู่แล้ว ไม่ต้องมี
    corrections.json แยกอีกต่อไป (ของเก่า ตัดออกแล้วตาม SKILL.md B3)
[ ] ซับไทย (.th.srt) พร้อมด้วย — แปลตามความหมาย ไม่ใช่คำต่อคำ, timing เดียวกับ .srt อังกฤษ,
    อัปเป็น subtitle track ที่สองใน YouTube (แพลตฟอร์มอื่นยังใส่หลายซับไม่ได้ เลยลงแค่ YouTube พอ)
[ ] ทุก scene มีภาพ ไม่มีจอว่าง/เฟรมค้างผิดจังหวะ (ดู final.mp4 จริงอย่างน้อย 1 รอบ)
[ ] Title / description / tags ครบ (EN) — ไม่ clickbait
[ ] Thumbnail อัปแล้ว สไตล์ตรงกับคลิป (flux2), อ่านออกบนมือถือ, ข้อความ ≤ 5 คำ
[ ] เพลง = channel blend จาก Music/ (ElevenLabs Music) → เช็กสิทธิ์ commercial/monetization + ไม่มี Content-ID claim ก่อนลง (ไม่ใช่ YouTube Audio Library แล้ว)
[ ] ถ้าใช้เสียง TTS/F5 → ติ๊ก altered-content disclosure ตอนอัปโหลด
[ ] End screen / subscribe
[ ] Nuay นอนพอ + ไม่ได้เร่งแบบฟุ้ง → ถ้าไม่ชัวร์ เลื่อนลงพรุ่งนี้
```

ที่มา: ปรับจาก SOP ใน Road data (SoilAndSignal) ให้ตรงกับ pipeline จริงของ repo นี้
