import json
import os

from transformers import pipeline

CONFIDENCE_THRESHOLD = 0.6

sentiment_model = pipeline(
    "sentiment-analysis",
    model="cardiffnlp/twitter-xlm-roberta-base-sentiment-multilingual"
)


def classify_sentiment(text):
    result = sentiment_model(text)[0]
    label = result["label"]
    score = result["score"]

    if score < CONFIDENCE_THRESHOLD:
        label = "uncertain"

    return {
        "raw_label": result["label"],
        "confidence": score,
        "trusted_label": label
    }


with open("output/transcript.json", "r") as file:
    transcript = json.load(file)

analyzed = []
for entry in transcript:
    sentiment = classify_sentiment(entry["text"])
    combined = {
        "start": entry["start"],
        "end": entry["end"],
        "text": entry["text"],
        "sentiment": sentiment
    }
    analyzed.append(combined)
    print(combined)

os.makedirs("output", exist_ok=True)
with open("output/analysis.json", "w") as file:
    json.dump(analyzed, file, indent=2)

print()
print("Saved analysis to output/analysis.json")
