import json
import os

from intent import classify_intent

RESULTS_FOLDER = "output/results"

result_files = [f for f in os.listdir(RESULTS_FOLDER) if f.endswith(".json")]

for filename in result_files:
    path = os.path.join(RESULTS_FOLDER, filename)
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

    summary = data["summary"]
    if summary.get("status") == "no_speech_detected":
        continue

    full_text = " ".join(entry["text"] for entry in data["lines"])
    new_intent = classify_intent(full_text)
    summary["intent"] = new_intent

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

    print(f"{filename}: {new_intent['trusted_intent']} (confidence={new_intent['confidence']:.2f})")
