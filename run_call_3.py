import json
import os

from analyze import classify_sentiment
from trend import compute_average, compute_trend
from intent import classify_intent
from escalate import assess_escalation

with open("output/transcript_call_3.json", "r", encoding="utf-8") as file:
    transcript = json.load(file)

analyzed_lines = []
scores = []
uncertain_count = 0

for entry in transcript:
    sentiment = classify_sentiment(entry["text"])
    analyzed_lines.append({
        "start": entry["start"],
        "end": entry["end"],
        "text": entry["text"],
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

    print(entry["text"])
    print(sentiment)
    print()

total_lines = len(transcript)
uncertain_ratio = uncertain_count / total_lines
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

print("SUMMARY:", summary)

os.makedirs("output", exist_ok=True)
with open("output/call_3_summary.json", "w", encoding="utf-8") as file:
    json.dump({"lines": analyzed_lines, "summary": summary}, file, indent=2)

print()
print("Saved to output/call_3_summary.json")
