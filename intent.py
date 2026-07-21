import json

from transformers import pipeline

CANDIDATE_INTENTS = [
    "order status",
    "complaint",
    "refund request",
    "technical issue",
    "general inquiry",
    "escalation request"
]

INTENT_CONFIDENCE_THRESHOLD = 0.4

intent_model = pipeline(
    "zero-shot-classification",
    model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"
)


def classify_intent(text):
    result = intent_model(text, CANDIDATE_INTENTS)
    top_intent = result["labels"][0]
    top_score = result["scores"][0]

    if top_score < INTENT_CONFIDENCE_THRESHOLD:
        trusted_intent = "uncertain"
    else:
        trusted_intent = top_intent

    return {
        "raw_intent": top_intent,
        "confidence": top_score,
        "trusted_intent": trusted_intent
    }


with open("output/transcript.json", "r") as file:
    transcript = json.load(file)

full_text = " ".join(entry["text"] for entry in transcript)
print("Full call text:")
print(full_text)
print()

call_intent = classify_intent(full_text)
print("Call-level intent:", call_intent)

with open("output/intent.json", "w") as file:
    json.dump(call_intent, file, indent=2)

print()
print("Saved intent result to output/intent.json")
