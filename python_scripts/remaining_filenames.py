import os 
import re
from datetime import datetime

# =========================
# CONFIG
# =========================
ROOT_DIR = "."
OUTPUT_FILE = "filename_and_folder_audit_report.txt"

# Only allow: letters, numbers, underscore, dash
VALID_PATTERN = re.compile(r'^[A-Za-z0-9_-]+$') 

# =========================
# VALIDATION RULE
# =========================
def is_invalid_name(name):
    """
    Checks:
    - spaces
    - full stops
    - invalid characters
    """

    if " " in name:
        return True

    if "." in name:
        return True

    if not VALID_PATTERN.match(name):
        return True

    return False


# =========================
# SCAN DIRECTORY
# =========================
def scan_directory(root_path):
    file_issues = []
    folder_issues = []

    for current_path, dirnames, filenames in os.walk(root_path):

        # Check folders
        for folder in dirnames:
            if is_invalid_name(folder):
                full_path = os.path.join(current_path, folder)
                folder_issues.append((folder, full_path))

        # Check files
        for file in filenames:
            name, _ext = os.path.splitext(file)
            if is_invalid_name(name):
                full_path = os.path.join(current_path, file)
                file_issues.append((file, full_path))

    return folder_issues, file_issues


# =========================
# REPORT GENERATOR
# =========================
def generate_report(folder_issues, file_issues):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = []
    lines.append("DIRECTORY NAME AUDIT REPORT")
    lines.append("=" * 60)
    lines.append(f"Scan Date : {now}")
    lines.append(f"Root Path : {os.path.abspath(ROOT_DIR)}")
    lines.append("")
    lines.append("Rules Applied:")
    lines.append(" - No spaces allowed")
    lines.append(" - No full stops in names")
    lines.append(" - Only A-Z a-z 0-9 _ - allowed")
    lines.append("")

    # =========================
    # FOLDERS SECTION
    # =========================
    lines.append("FOLDERS WITH ISSUES")
    lines.append("-" * 60)

    if not folder_issues:
        lines.append("No folder issues found.")
    else:
        for i, (name, path) in enumerate(sorted(folder_issues), start=1):
            lines.append(f"{i:04d}. {name}")
            lines.append(f"      Path: {path}")
            lines.append("")

    # =========================
    # FILES SECTION
    # =========================
    lines.append("")
    lines.append("FILES WITH ISSUES")
    lines.append("-" * 60)

    if not file_issues:
        lines.append("No file issues found.")
    else:
        for i, (name, path) in enumerate(sorted(file_issues), start=1):
            lines.append(f"{i:04d}. {name}")
            lines.append(f"      Path: {path}")
            lines.append("")

    # =========================
    # SUMMARY
    # =========================
    lines.append("")
    lines.append("SUMMARY")
    lines.append("-" * 60)
    lines.append(f"Total Folder Issues : {len(folder_issues)}")
    lines.append(f"Total File Issues   : {len(file_issues)}")
    lines.append(f"TOTAL ISSUES        : {len(folder_issues) + len(file_issues)}")

    return "\n".join(lines)


# =========================
# RUN
# =========================
if __name__ == "__main__":
    folders, files = scan_directory(ROOT_DIR)
    report = generate_report(folders, files)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"Report generated: {OUTPUT_FILE}")