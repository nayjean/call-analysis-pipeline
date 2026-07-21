import json
import os
import time

from dotenv import load_dotenv
from openai import OpenAI
from google import genai

from analyze import classify_sentiment

load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

PROMPT_TEMPLATE = """Classify the sentiment of this customer service call line as exactly one of: positive, negative, neutral.
Also give your confidence as a number between 0 and 1.
Respond ONLY with JSON in this exact format: {{"label": "...", "confidence": ...}}

Line: "{text}"
"""


def classify_with_openai(text):
    start = time.time()
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": PROMPT_TEMPLATE.format(text=text)}]
    )
    elapsed = time.time() - start

    raw = response.choices[0].message.content
    parsed = json.loads(raw)

    return {
        "label": parsed["label"],
        "confidence": parsed["confidence"],
        "time_seconds": round(elapsed, 2)
    }


def classify_with_gemini(text):
    start = time.time()
    response = gemini_client.models.generate_content(
        model="gemini-2.0-flash",
        contents=PROMPT_TEMPLATE.format(text=text)
    )
    elapsed = time.time() - start

    raw = response.text.strip()
    if raw.startswith("```"):
        raw = raw.strip("`").replace("json", "", 1).strip()
    parsed = json.loads(raw)

    return {
        "label": parsed["label"],
        "confidence": parsed["confidence"],
        "time_seconds": round(elapsed, 2)
    }


def classify_with_local_model(text):
    start = time.time()
    result = classify_sentiment(text)
    elapsed = time.time() - start

    return {
        "label": result["raw_label"],
        "confidence": result["confidence"],
        "time_seconds": round(elapsed, 2)
    }


if __name__ == "__main__":
    with open("output/transcript_call_3.json", "r", encoding="utf-8") as file:
        transcript = json.load(file)

    sample_lines = transcript[:8]

    comparison = []
    for entry in sample_lines:
        text = entry["text"]
        print("LINE:", text)

        local_result = classify_with_local_model(text)

        try:
            openai_result = classify_with_openai(text)
        except Exception as error:
            openai_result = {"error": str(error)}

        try:
            gemini_result = classify_with_gemini(text)
        except Exception as error:
            gemini_result = {"error": str(error)}

        print("  Local :", local_result)
        print("  OpenAI:", openai_result)
        print("  Gemini:", gemini_result)
        print()

        comparison.append({
            "text": text,
            "local": local_result,
            "openai": openai_result,
            "gemini": gemini_result
        })

    with open("output/sentiment_comparison.json", "w", encoding="utf-8") as file:
        json.dump(comparison, file, indent=2)

    print("Saved comparison to output/sentiment_comparison.json")
