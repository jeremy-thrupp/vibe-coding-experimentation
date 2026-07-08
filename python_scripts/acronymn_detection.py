import os
import re
import enchant
from datetime import datetime

# =========================
# CONFIG
# =========================
ROOT_DIR = "."
OUTPUT_FILE = "possible_acronyms.txt"

dictionary = enchant.Dict("en_US")

KNOWN_ACRONYMS = {
    "API", "HTTP", "HTTPS", "JSON", "XML", "SQL",
    "JWT", "PDF", "CSV", "HTML", "CSS", "UI", "UX",
    "ID", "URL", "IP", "DB", "CPU", "GPU", "VS"
}

# =========================
# TOKEN SPLIT
# =========================
def split_name(name):
    # remove extension
    name = os.path.splitext(name)[0]

    # split camelCase
    name = re.sub(r"([a-z])([A-Z])", r"\1 \2", name)
    name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", name)

    # replace ANY non-alphanumeric character with space
    # (this handles: (), [], {}, commas, dots, dashes, etc.)
    name = re.sub(r"[^A-Za-z0-9]+", " ", name)

    return name.split()

# =========================
# STRONG FILTERS
# =========================
def is_noise(token):
    if token.isdigit():
        return True

    noise = {"THE", "TO", "AND", "FOR", "WITH", "THIS", "THAT"}
    if token.upper() in noise:
        return True

    return False

# =========================
# REAL ACRONYM DETECTION
# =========================
def is_likely_acronym(token):
    t = token.strip()

    if is_noise(t):
        return False

    if len(t) < 2 or len(t) > 6:
        return False

    # Known acronyms
    if t.upper() in KNOWN_ACRONYMS:
        return True

    # ALL CAPS = strong signal
    if t.isupper():
        return True

    # Reject normal dictionary words
    if t.isalpha() and dictionary.check(t.lower()):
        return False

    # Consonant-heavy heuristic
    vowels = set("aeiouAEIOU")
    vowel_count = sum(1 for c in t if c in vowels)

    if vowel_count <= 1:
        return True

    return False

# =========================
# TRAVERSAL
# =========================
def traverse(root_dir):
    acronyms = set()

    for root, dirs, files in os.walk(root_dir):
        for name in dirs + files:
            tokens = split_name(name)

            for t in tokens:
                if is_likely_acronym(t):
                    acronyms.add(t.upper())

    return acronyms

# =========================
# OUTPUT
# =========================
def write_output(acronyms, root_dir):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    acronyms = sorted(acronyms)

    grouped = {}
    for a in acronyms:
        key = a[0]
        grouped.setdefault(key, []).append(a)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:

        # HEADER
        f.write("========================================\n")
        f.write(" ACRONYM REPORT\n")
        f.write("========================================\n")
        f.write(f"Scan time   : {now}\n")
        f.write(f"Root folder : {os.path.abspath(root_dir)}\n")
        f.write(f"Total found : {len(acronyms)}\n")
        f.write("========================================\n\n")

        # GROUPED SECTION
        for letter in sorted(grouped.keys()):
            f.write(f"[{letter}]\n")
            f.write("-" * 40 + "\n")

            for a in grouped[letter]:
                f.write(f"{a}\n")

            f.write("\n")

        # QUICK ONE-LINER SUMMARY
        f.write("========================================\n")
        f.write(" QUICK LIST (SPACE-SEPARATED)\n")
        f.write("========================================\n")
        f.write(" ".join(acronyms) + "\n\n")

        # FOOTER
        f.write("========================================\n")
        f.write("END OF REPORT\n") 
        f.write("========================================\n")

# =========================
# MAIN
# =========================
if __name__ == "__main__":
    results = traverse(ROOT_DIR)
    write_output(results, ROOT_DIR)

    print(f"Found {len(results)} acronyms")
    print(f"Saved to {OUTPUT_FILE}")