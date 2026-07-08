import os
from collections import defaultdict

OUTPUT_FILE = "directory_report.txt"

def analyze_directory(root_path="."):
    folder_count = 0
    depth_counts = defaultdict(int)
    max_depth = 0

    lines = []

    for current_path, dirnames, filenames in os.walk(root_path):
        relative_path = os.path.relpath(current_path, root_path)
        depth = 0 if relative_path == "." else relative_path.count(os.sep) + 1

        folder_count += len(dirnames)
        depth_counts[depth] += len(dirnames)
        max_depth = max(max_depth, depth)

    # =========================
    # BUILD REPORT
    # =========================
    lines.append("=" * 60)
    lines.append(" DIRECTORY STRUCTURE REPORT")
    lines.append("=" * 60)
    lines.append(f"Root Directory: {os.path.abspath(root_path)}")
    lines.append(f"Total Folders (including subfolders): {folder_count}")
    lines.append(f"Maximum Depth: {max_depth}")
    lines.append("")
    lines.append("Breakdown by depth level:")

    for d in range(max_depth + 1):
        lines.append(f"  Depth {d}: {depth_counts[d]} folder(s)")

    lines.append("=" * 60)  

    # =========================
    # WRITE TO FILE
    # =========================
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Report written to: {OUTPUT_FILE}")


if __name__ == "__main__":
    analyze_directory(".")