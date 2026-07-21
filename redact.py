import json
import re

from transformers import pipeline

ner_model = pipeline(
    "ner",
    model="dslim/bert-base-NER",
    aggregation_strategy="simple"
)

NER_REDACT_TYPES = {
    "ORG": "[COMPANY]"
}

KNOWN_TERMS = {
    "blackberry": "[COMPANY]",
    "blackberrys": "[COMPANY]"
}


def redact_with_ner(text):
    entities = ner_model(text)

    entities_to_redact = [e for e in entities if e["entity_group"] in NER_REDACT_TYPES]
    entities_to_redact.sort(key=lambda e: e["start"], reverse=True)

    redacted = text
    for entity in entities_to_redact:
        placeholder = NER_REDACT_TYPES[entity["entity_group"]]
        redacted = redacted[:entity["start"]] + placeholder + redacted[entity["end"]:]

    return redacted


def redact_known_terms(text):
    redacted = text
    for term, placeholder in KNOWN_TERMS.items():
        pattern = re.compile(re.escape(term), re.IGNORECASE)
        redacted = pattern.sub(placeholder, redacted)
    return redacted


def redact_text(text):
    redacted = redact_with_ner(text)
    redacted = redact_known_terms(redacted)
    return redacted


if __name__ == "__main__":
    with open("output/transcript_call_3.json", "r", encoding="utf-8") as file:
        transcript = json.load(file)

    redacted_transcript = []
    for entry in transcript:
        redacted_text = redact_text(entry["text"])
        redacted_transcript.append({
            "start": entry["start"],
            "end": entry["end"],
            "text": redacted_text
        })
        print(redacted_text)

    with open("output/transcript_call_3_redacted.json", "w", encoding="utf-8") as file:
        json.dump(redacted_transcript, file, indent=2)

    print()
    print("Saved redacted transcript to output/transcript_call_3_redacted.json")
