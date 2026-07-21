import json
import os

from faster_whisper import WhisperModel

model = WhisperModel("base", device="cpu", compute_type="int8")

segments, info = model.transcribe("sample_call.mp3")

print("Detected language:", info.language)
print()

transcript = []
for segment in segments:
    entry = {
        "start": segment.start,
        "end": segment.end,
        "text": segment.text.strip()
    }
    transcript.append(entry)
    print(f"[{entry['start']:.2f}s -> {entry['end']:.2f}s] {entry['text']}")

os.makedirs("output", exist_ok=True)

with open("output/transcript.json", "w") as file:
    json.dump(transcript, file, indent=2)

print()
print("Saved transcript to output/transcript.json")
