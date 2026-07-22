import json
import os

from escalate import assess_escalation

RESULTS_FOLDER = "output/results"

result_files = [f for f in os.listdir(RESULTS_FOLDER) if f.endswith(".json")]

for filename in result_files:
    path = os.path.join(RESULTS_FOLDER, filename)
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

    summary = data["summary"]
    if summary.get("status") == "no_speech_detected":
        continue

    new_escalation = assess_escalation(
        data["lines"],
        summary["trend"],
        summary["overall_average_sentiment"]
    )
    summary["escalation"] = new_escalation

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

    print(f"{filename}: {new_escalation['escalation_level']} (score={new_escalation['escalation_score']})")
