import re

def split_sentences(text):
    # Remove email headers
    text = re.sub(r"^.*?Subject:.*?\n", "", text, flags=re.DOTALL)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    # Split on real sentence endings
    sentences = re.split(r'(?<=[.!?])\s+', text)

    # Keep only meaningful sentences
    clean = []
    for s in sentences:
        s = s.strip()
        if len(s) < 30:
            continue
        if s.lower().startswith(("hi", "hello", "thanks", "best regards")):
            continue
        clean.append(s)

    return clean
