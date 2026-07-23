STRONG_KEYWORDS = ["angry", "unacceptable", "manager"]
WEAK_KEYWORDS = ["frustrat", "escalate", "complaint"]

STRONG_KEYWORD_WEIGHT = 40
WEAK_KEYWORD_WEIGHT = 15
NEGATIVE_SENTIMENT_WEIGHT = 30
DECLINING_TREND_WEIGHT = 20
NEGATIVE_RATIO_WEIGHT = 10

NEGATIVE_SENTIMENT_THRESHOLD = -0.3
NEGATIVE_RATIO_THRESHOLD = 0.3


def find_keyword_matches(lines, keywords):
    hits = 0
    matched_lines = []

    for entry in lines:
        text = entry["text"].lower()
        for keyword in keywords:
            if keyword in text:
                hits += 1
                matched_lines.append(entry["text"])
                break

    return hits, matched_lines


def get_customer_lines(lines):
    speakers = {entry.get("speaker") for entry in lines}
    speakers.discard(None)

    if len(speakers) < 2:
        return lines

    agent_speaker = lines[0]["speaker"]
    return [entry for entry in lines if entry["speaker"] != agent_speaker]


def compute_negative_ratio(lines):
    trusted_lines = [e for e in lines if e["sentiment"]["trusted_label"] != "uncertain"]
    if len(trusted_lines) == 0:
        return 0

    negative_lines = [e for e in trusted_lines if e["sentiment"]["trusted_label"] == "negative"]
    return len(negative_lines) / len(trusted_lines)


def assess_escalation(analyzed_lines, trend, overall_average_sentiment):
    score = 0
    reasons = []

    customer_lines = get_customer_lines(analyzed_lines)
    strong_hits, strong_matches = find_keyword_matches(customer_lines, STRONG_KEYWORDS)
    weak_hits, weak_matches = find_keyword_matches(customer_lines, WEAK_KEYWORDS)

    if strong_hits > 0:
        score += STRONG_KEYWORD_WEIGHT
        reasons.append(f"{strong_hits} line(s) matched strong escalation keywords: {strong_matches}")
    elif weak_hits > 0:
        score += WEAK_KEYWORD_WEIGHT
        reasons.append(f"{weak_hits} line(s) matched weak/ambiguous escalation keywords: {weak_matches}")

    if overall_average_sentiment is not None and overall_average_sentiment < NEGATIVE_SENTIMENT_THRESHOLD:
        score += NEGATIVE_SENTIMENT_WEIGHT
        reasons.append(f"overall sentiment ({overall_average_sentiment:.2f}) below threshold")

    if trend == "declining":
        score += DECLINING_TREND_WEIGHT
        reasons.append("sentiment trend is declining across the call")

    negative_ratio = compute_negative_ratio(analyzed_lines)
    if negative_ratio > NEGATIVE_RATIO_THRESHOLD:
        score += NEGATIVE_RATIO_WEIGHT
        reasons.append(f"{negative_ratio:.0%} of trusted lines were negative")

    if score >= 60:
        level = "High"
    elif score >= 30:
        level = "Medium"
    else:
        level = "Low"

    return {
        "escalation_score": score,
        "escalation_level": level,
        "reasons": reasons
    }
