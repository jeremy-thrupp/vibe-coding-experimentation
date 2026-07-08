import os
from datetime import datetime

# =========================
# CONFIG
# =========================
ROOT_DIR = "."
OUTPUT_FILE = "recommended_file_deletions.txt" 

# =========================
# CATEGORIES
# =========================
CATEGORIES = {
    "Shortcuts": {".lnk", ".url"},
    "Executables (Optional Review)": {".exe", ".msi", ".bat", ".cmd", ".com", ".scr"},
    "Temporary Files (Optional Review)": {".tmp", ".temp"},
    "Logs (Optional Review)": {".log"},
    "Archives (Optional Review)": {".zip", ".rar", ".7z", ".tar", ".gz"},
    "Python Cache (Optional Review)": {"__pycache__"},
    "System Junk (Optional Review)": {"thumbs.db", ".ds_store"},
    "Office Temp Files (Optional Review)": {"~$"},
}

# =========================
# STORAGE
# =========================
results = {category: [] for category in CATEGORIES}
results["Other Suspicious Files"] = []

# =========================
# HELPERS
# =========================
def classify_file(file_path):
    filename = os.path.basename(file_path).lower()
    ext = os.path.splitext(filename)[1].lower()

    # Folder-based checks
    if "__pycache__" in file_path:
        return "Python Cache"

    if filename in ["thumbs.db", ".ds_store"]:
        return "System Junk"

    # Office temp files
    if filename.startswith("~$"):
        return "Office Temp Files"

    # Extension-based checks
    for category, extensions in CATEGORIES.items():
        if ext in extensions:
            return category

    return None


# =========================
# SCAN FILE SYSTEM
# =========================
for root, dirs, files in os.walk(ROOT_DIR):
    for file in files:
        full_path = os.path.join(root, file)
        category = classify_file(full_path)

        if category:
            results[category].append(full_path)
        else:
            # Optional: flag unknown risky patterns
            if file.endswith("~") or file.endswith(".bak"):
                results["Other Suspicious Files"].append(full_path)

# =========================
# WRITE OUTPUT
# =========================
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:

    # ---- HEADER ----
    f.write("========================================\n")
    f.write("        FILE CLEANUP REPORT\n")
    f.write("========================================\n\n")

    f.write(f"Scan Root Directory: {os.path.abspath(ROOT_DIR)}\n")
    f.write(f"Generated On       : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write("Mode               : Recommendation Only (No files deleted)\n")
    f.write("\n")

    f.write("This report lists files that are may be deleted if you have approved them.\n")
    f.write("Always verify before deleting anything.\n")
    f.write("\n")
    f.write("=" * 40 + "\n\n")

    # ---- CONTENT ----
    for category, items in results.items():
        if not items:
            continue

        f.write(f"{category}:\n")
        f.write("-" * len(category) + "\n")

        for item in sorted(items):
            f.write(item + "\n")

        f.write("\n")

print(f"Scan complete. Results saved to {OUTPUT_FILE}")