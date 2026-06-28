"""Validate script.json output from /faceless-short skill."""
import sys, json, pathlib

REQUIRED = ["slug", "topic", "hook", "explain", "illustrate", "teach",
            "narration", "word_count", "est_duration_sec"]

def validate(json_path):
    path = pathlib.Path(json_path)
    if not path.exists():
        return [f"file not found: {json_path}"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"invalid JSON: {e}"]
    errors = []
    for field in REQUIRED:
        if field not in data:
            errors.append(f"missing field: {field}")
        elif isinstance(data[field], str) and not data[field].strip():
            errors.append(f"empty string: {field}")
    if "word_count" in data:
        wc = data["word_count"]
        if not isinstance(wc, (int, float)):
            errors.append(f"word_count must be a number, got: {type(wc).__name__}")
        else:
            if wc < 80:
                errors.append(f"word_count={wc} below 80 (too short)")
            if wc > 140:
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
