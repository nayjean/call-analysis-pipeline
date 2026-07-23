import json
import os

from deepgram_transcribe import transcribe_with_diarization
from analyze import classify_sentiment
from trend import compute_average, compute_trend
from intent import classify_intent
from escalate import assess_escalation

INPUT_FOLDER = "calls"
OUTPUT_FOLDER = "output/results"
AUDIO_EXTENSIONS = (".mp3", ".wav", ".m4a")


def process_call(filepath):
    transcript = transcribe_with_diarization(filepath)

    if len(transcript) == 0:
        return {
            "lines": [],
            "summary": {
                "status": "no_speech_detected"
            }
        }

    analyzed_lines = []
    scores = []
    uncertain_count = 0

    for entry in transcript:
        sentiment = classify_sentiment(entry["text"])
        analyzed_lines.append({
            "start": entry["start"],
            "end": entry["end"],
            "text": entry["text"],
            "speaker": entry.get("speaker"),
            "sentiment": sentiment
        })

        if sentiment["trusted_label"] == "uncertain":
            uncertain_count += 1
        elif sentiment["trusted_label"] == "positive":
            scores.append(1)
        elif sentiment["trusted_label"] == "negative":
            scores.append(-1)
        else:
            scores.append(0)

    total_lines = len(transcript)
    uncertain_ratio = uncertain_count / total_lines if total_lines > 0 else 0
    overall_confidence = "low" if uncertain_ratio > 0.5 else "high"

    full_text = " ".join(entry["text"] for entry in transcript)
    call_intent = classify_intent(full_text)

    overall_average_sentiment = compute_average(scores)
    trend = compute_trend(scores)
    escalation = assess_escalation(analyzed_lines, trend, overall_average_sentiment)

    summary = {
        "total_lines": total_lines,
        "uncertain_lines": uncertain_count,
        "uncertain_ratio": round(uncertain_ratio, 2),
        "overall_average_sentiment": overall_average_sentiment,
        "trend": trend,
        "overall_confidence": overall_confidence,
        "intent": call_intent,
        "escalation": escalation
    }

    return {"lines": analyzed_lines, "summary": summary}


if __name__ == "__main__":
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    audio_files = [f for f in os.listdir(INPUT_FOLDER) if f.lower().endswith(AUDIO_EXTENSIONS)]
    print(f"Found {len(audio_files)} audio file(s) in '{INPUT_FOLDER}'")
    print()

    for filename in audio_files:
        filepath = os.path.join(INPUT_FOLDER, filename)
        call_id = os.path.splitext(filename)[0]
        output_path = os.path.join(OUTPUT_FOLDER, f"{call_id}.json")

        if os.path.exists(output_path):
            print(f"Skipping {filename} (already processed)")
            print()
            continue

        print(f"Processing {filename}...")

        try:
            result = process_call(filepath)

            with open(output_path, "w", encoding="utf-8") as file:
                json.dump(result, file, indent=2)

            if result["summary"].get("status") == "no_speech_detected":
                print(f"  Done. No speech detected. Saved to {output_path}")
            else:
                escalation_level = result["summary"]["escalation"]["escalation_level"]
                print(f"  Done. Escalation: {escalation_level}. Saved to {output_path}")

        except Exception as error:
            print(f"  FAILED: {error}")

        print()
