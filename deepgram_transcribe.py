import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("DEEPGRAM_API_KEY")

URL = "https://api.deepgram.com/v1/listen"
PARAMS = {
    "model": "nova-2",
    "detect_language": "true",
    "punctuate": "true",
    "smart_format": "true",
    "utterances": "true"
}


def transcribe_with_deepgram(filename):
    with open(filename, "rb") as audio_file:
        audio_data = audio_file.read()

    headers = {
        "Authorization": f"Token {API_KEY}",
        "Content-Type": "audio/mp3"
    }

    response = requests.post(URL, params=PARAMS, headers=headers, data=audio_data)
    result = response.json()

    utterances = result["results"]["utterances"]

    transcript = []
    for utterance in utterances:
        transcript.append({
            "start": utterance["start"],
            "end": utterance["end"],
            "text": utterance["transcript"]
        })

    return transcript


def transcribe_with_diarization(filename):
    with open(filename, "rb") as audio_file:
        audio_data = audio_file.read()

    headers = {
        "Authorization": f"Token {API_KEY}",
        "Content-Type": "audio/mp3"
    }

    params = dict(PARAMS)
    params["diarize"] = "true"

    response = requests.post(URL, params=params, headers=headers, data=audio_data)
    result = response.json()

    utterances = result["results"]["utterances"]

    transcript = []
    for utterance in utterances:
        transcript.append({
            "start": utterance["start"],
            "end": utterance["end"],
            "text": utterance["transcript"],
            "speaker": utterance.get("speaker")
        })

    return transcript


if __name__ == "__main__":
    transcript = transcribe_with_deepgram("sample_call_3.mp3")

    for entry in transcript:
        print(f"[{entry['start']:.2f}s -> {entry['end']:.2f}s] {entry['text']}")

    os.makedirs("output", exist_ok=True)
    with open("output/transcript_call_3.json", "w", encoding="utf-8") as file:
        json.dump(transcript, file, indent=2)

    print()
    print("Saved to output/transcript_call_3.json")
