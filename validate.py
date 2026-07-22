import csv
import json
import os

RESULTS_FOLDER = "output/results"
GROUND_TRUTH_FILE = "output/ground_truth_template.csv"


def load_ground_truth():
    with open(GROUND_TRUTH_FILE, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    for row in rows:
        for key in row:
            row[key] = row[key].strip().lower()

    return rows


def load_prediction(call_id):
    path = os.path.join(RESULTS_FOLDER, f"{call_id}.json")
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data["summary"]


ground_truth = load_ground_truth()

escalation_correct = 0
trend_correct = 0
total = 0

print(f"{'Call':<16}{'Escalation (exp/got)':<26}{'Trend (exp/got)':<26}{'Intent (expected -> predicted)'}")
print("-" * 110)

for row in ground_truth:
    call_id = row["call_id"]
    summary = load_prediction(call_id)

    predicted_escalation = summary["escalation"]["escalation_level"].lower()
    predicted_trend = summary["trend"].lower()
    predicted_intent = summary["intent"]["trusted_intent"]

    escalation_match = "OK" if predicted_escalation == row["expected_escalation"] else "X"
    trend_match = "OK" if predicted_trend == row["expected_trend"] else "X"

    if escalation_match == "OK":
        escalation_correct += 1
    if trend_match == "OK":
        trend_correct += 1
    total += 1

    print(f"{call_id:<16}"
          f"{row['expected_escalation'] + '/' + predicted_escalation + ' ' + escalation_match:<26}"
          f"{row['expected_trend'] + '/' + predicted_trend + ' ' + trend_match:<26}"
          f"{row['expected_intent']} -> {predicted_intent}")

print()
print(f"Escalation accuracy: {escalation_correct}/{total} ({escalation_correct / total:.0%})")
print(f"Trend accuracy: {trend_correct}/{total} ({trend_correct / total:.0%})")
