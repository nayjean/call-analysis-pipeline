from deepgram_transcribe import transcribe_with_diarization
from escalate import STRONG_KEYWORDS, WEAK_KEYWORDS, find_keyword_matches

TEST_CALLS = ["calls/audio_4.mp3", "calls/audio_7.mp3"]

for filepath in TEST_CALLS:
    print(f"=== {filepath} ===")
    transcript = transcribe_with_diarization(filepath)

    for entry in transcript:
        print(f"  speaker {entry['speaker']}: {entry['text'][:90]}")

    first_speaker = transcript[0]["speaker"]
    print(f"  (assuming speaker {first_speaker} is the agent, since they spoke first)")

    customer_lines = [e for e in transcript if e["speaker"] != first_speaker]

    all_strong, _ = find_keyword_matches(transcript, STRONG_KEYWORDS)
    all_weak, all_weak_matches = find_keyword_matches(transcript, WEAK_KEYWORDS)
    cust_strong, _ = find_keyword_matches(customer_lines, STRONG_KEYWORDS)
    cust_weak, cust_weak_matches = find_keyword_matches(customer_lines, WEAK_KEYWORDS)

    print(f"  All-speaker keyword hits: strong={all_strong}, weak={all_weak} {all_weak_matches}")
    print(f"  Customer-only keyword hits: strong={cust_strong}, weak={cust_weak} {cust_weak_matches}")
    print()
