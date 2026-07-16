def read_transcript(filename):
    with open(filename, "r") as file:
        return file.read()


def count_words(text):
    words = text.split()
    return len(words)


def get_lines(text):
    lines = text.split("\n")
    lines = [line for line in lines if line.strip() != ""]
    return lines


def analyze_line(line, keywords):
    matched = []
    for keyword in keywords:
        if keyword in line.lower():
            matched.append(keyword)

    result = {
        "line": line,
        "flag_count": len(matched),
        "matched_keywords": matched
    }
    return result


text = read_transcript("sample_transcript.txt")
total_words = count_words(text)
lines = get_lines(text)

keywords = ["frustrat", "escalate", "angry", "unacceptable"]

results = []
for line in lines:
    result = analyze_line(line, keywords)
    results.append(result)

print("Total words:", total_words)
print()
for result in results:
    print(result)
