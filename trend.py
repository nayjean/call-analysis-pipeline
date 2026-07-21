import json
import os

UNCERTAIN_RATIO_THRESHOLD = 0.5


def sentiment_to_score(trusted_label):
    if trusted_label == "positive":
        return 1
    elif trusted_label == "negative":
        return -1
    elif trusted_label == "neutral":
        return 0
    else:
        return None


with open("output/analysis.json", "r") as file:
    analyzed = json.load(file)

scores = []
uncertain_count = 0

for entry in analyzed:
    trusted_label = entry["sentiment"]["trusted_label"]
    score = sentiment_to_score(trusted_label)

    if score is None:
        uncertain_count += 1
    else:
        scores.append(score)

total_lines = len(analyzed)
uncertain_ratio = uncertain_count / total_lines

print("Total lines:", total_lines)
print("Uncertain lines:", uncertain_count)
print("Uncertain ratio:", round(uncertain_ratio, 2))
print("Trusted scores:", scores)


def compute_average(score_list):
    if len(score_list) == 0:
        return None
    return sum(score_list) / len(score_list)


def compute_trend(score_list):
    if len(score_list) < 2:
        return "not enough data"

    midpoint = len(score_list) // 2
    first_half = score_list[:midpoint]
    second_half = score_list[midpoint:]

    first_avg = compute_average(first_half)
    second_avg = compute_average(second_half)

    difference = second_avg - first_avg

    if difference > 0.2:
        return "improving"
    elif difference < -0.2:
        return "declining"
    else:
        return "stable"


overall_average = compute_average(scores)
trend = compute_trend(scores)

if uncertain_ratio > UNCERTAIN_RATIO_THRESHOLD:
    overall_confidence = "low"
else:
    overall_confidence = "high"

print()
print("Overall average sentiment:", overall_average)
print("Trend:", trend)
print("Overall confidence:", overall_confidence)

summary = {
    "total_lines": total_lines,
    "uncertain_lines": uncertain_count,
    "uncertain_ratio": round(uncertain_ratio, 2),
    "overall_average_sentiment": overall_average,
    "trend": trend,
    "overall_confidence": overall_confidence
}

call_result = {
    "lines": analyzed,
    "summary": summary
}

os.makedirs("output", exist_ok=True)
with open("output/call_summary.json", "w") as file:
    json.dump(call_result, file, indent=2)

print()
print("Saved consolidated call summary to output/call_summary.json")
