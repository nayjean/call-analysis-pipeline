import json
import os

RESULTS_FOLDER = "output/results"

result_files = [f for f in os.listdir(RESULTS_FOLDER) if f.endswith(".json")]

print(f"{'Call':<18}{'Status':<12}{'Trend':<12}{'Sentiment':<12}{'Intent':<32}{'Escalation':<12}")
print("-" * 98)

for filename in sorted(result_files):
    with open(os.path.join(RESULTS_FOLDER, filename), "r", encoding="utf-8") as file:
        data = json.load(file)

    call_id = filename.replace(".json", "")
    summary = data["summary"]

    if summary.get("status") == "no_speech_detected":
        print(f"{call_id:<18}{'no_speech':<12}")
        continue

    trend = summary["trend"]
    sentiment = round(summary["overall_average_sentiment"], 2)
    intent = summary["intent"]["trusted_intent"]
    escalation = summary["escalation"]["escalation_level"]

    print(f"{call_id:<18}{'ok':<12}{trend:<12}{sentiment:<12}{intent:<32}{escalation:<12}")

print()
print("Calls flagged Medium/High escalation, with reasons:")
for filename in sorted(result_files):
    with open(os.path.join(RESULTS_FOLDER, filename), "r", encoding="utf-8") as file:
        data = json.load(file)

    summary = data["summary"]
    if summary.get("status") == "no_speech_detected":
        continue

    escalation = summary["escalation"]
    if escalation["escalation_level"] in ("Medium", "High"):
        call_id = filename.replace(".json", "")
        print(f"  {call_id}: score={escalation['escalation_score']}, reasons={escalation['reasons']}")
