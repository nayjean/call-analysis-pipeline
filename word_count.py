with open("sample_transcript.txt", "r") as file:
    text = file.read()

words = text.split()
word_count = len(words)

print("Total words:", word_count)
