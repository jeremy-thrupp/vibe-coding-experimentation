import os
import re
import sys
import ctypes
from ctypes import wintypes

# =========================
# CONFIGURATION
# =========================
DRY_RUN = True
PREVIEW_FILE = "rename_preview.txt"

# 0 = unlimited depth
MAX_DEPTH = 0

# =========================
# EXCLUDED FOLDERS
# =========================
EXCLUDED_PATHS = {
    "node_modules",
    ".git",
    "venv",
    "__pycache__",
    "build",
    "dist",
    "DoNotRename",
    "archive/old_files",
    r"C:\Users\Scripts",
    r"D:\Backup\DoNotTouch"
}

EXCLUDED_PATHS = {
    os.path.normpath(os.path.abspath(p)).lower()
    for p in EXCLUDED_PATHS
}

# =========================
# ACRONYMS
# =========================
INCLUDED_ACRONYMS = "PDF SY"
INCLUDED_ACRONYMS = set(INCLUDED_ACRONYMS.lower().split())

# =========================
# CLI FLAGS
# =========================
args = {arg.lower() for arg in sys.argv[1:]}

if "dry-run-false" in args:
    DRY_RUN = False

HIDE_FOLDERS_FROM_PREVIEW = False
if "hide-folders-from-preview" in args:
    HIDE_FOLDERS_FROM_PREVIEW = True

RUNTIME_EXCLUDED_NAMES = {
    arg for arg in sys.argv[1:]
    if arg.lower() != "dry-run-false"
    and arg.lower() != "hide-folders-from-preview"
}

# =========================
# EXCLUSIONS
# =========================
EXCLUDED_NAMES = {
    "appdata", "desktop.ini", "thumbs.db", "ntuser.dat",
    "ntuser.dat.log", "ntuser.ini", "iconcache.db",
    "onedrive", "onedrive temp", "desktop", "documents",
    "pictures", "camera roll", "saved pictures",
    "onedrivecache", "onedrivetemp", "sync", "sync root",
    "odls", "odl", ".ds_store", "conflict",
    "conflicted copy", "google drive", "drivefs",
    "drive file stream", "google drive file stream",
    "drivefs_tmp", "syncdb", "metadata", "snapshot",
    "journals", "temporary items", "temp", "cache",
    "caches", "offline", "offline cache",
}

EXCLUDED_EXTENSIONS = {
    ".lnk", ".url", ".ini", ".sys", ".dll", ".exe",
    ".msi", ".dat", ".log", ".ds_store", ".crdownload",
    ".part", ".tmp"
}

def should_exclude(name: str) -> bool:
    if name.startswith("."):
        return True

    if name.lower() in EXCLUDED_NAMES:
        return True

    _, ext = os.path.splitext(name)
    return ext.lower() in EXCLUDED_EXTENSIONS

# =========================
# PATH EXCLUSION
# =========================
def is_in_excluded_path(path: str) -> bool:
    path = os.path.normpath(os.path.abspath(path)).lower()

    for excluded in EXCLUDED_PATHS:
        if path == excluded or path.startswith(excluded + os.sep):
            return True

    return False

# =========================
# NAME TRANSFORMATION
# =========================
def transform_name(name: str) -> str:
    base, ext = os.path.splitext(name)

    base = base.replace(".", "-")
    base = base.replace(",", "-")
    base = base.replace("&", "and")
    base = re.sub(r'[<>:"/\\|?*\[\]()!;\'`]', "", base)
    base = re.sub(r"[\s_]+", "-", base)
    base = re.sub(r"-{2,}", "-", base)
    base = base.strip("-")

    tokens = re.split(r"(-)", base)

    small_words = {
        "a", "an", "the", "and", "but", "or", "nor", "for",
        "so", "yet", "as", "at", "by", "in", "of", "on",
        "to", "up", "with", "from", "into", "onto", "over",
        "under", "between", "without", "within"
    }

    def transform_segment(segment):
        parts = segment.split("+")
        return "+".join(part.upper() for part in parts if part)

    transformed = []

    for token in tokens:
        if token == "-":
            transformed.append("-")
            continue

        subparts = token.split("-")
        rebuilt = []

        for i, sub in enumerate(subparts):
            if not sub:
                continue

            lower = sub.lower()

            if "+" in sub:
                rebuilt.append(transform_segment(sub))
            elif lower in INCLUDED_ACRONYMS:
                rebuilt.append(sub.upper())
            elif i == 0:
                rebuilt.append(lower.capitalize())
            elif lower in small_words:
                rebuilt.append(lower)
            else:
                rebuilt.append(lower.capitalize())

        transformed.append("-".join(rebuilt))

    return f"{''.join(transformed)}{ext}"

# =========================
# METADATA PRESERVATION
# =========================
def preserve_metadata(dst, src_stat):
    os.utime(dst, (src_stat.st_atime, src_stat.st_mtime))

# =========================
# DEPTH
# =========================
def get_depth(path: str) -> int:
    rel = os.path.relpath(path, ".")
    return 0 if rel == "." else rel.count(os.sep) + 1

# =========================
# MAIN
# =========================
def main():
    rename_list = []
    keep_list = []
    skip_list = []
    folder_timestamps = {}
    folder_renames = {}

    seen_cli_items = set()

    # 🔹 Capture folder timestamps BEFORE changes
    for root, dirs, _ in os.walk(".", topdown=True):
        for d in dirs:
            full_path = os.path.abspath(os.path.join(root, d))
            try:
                stat = os.stat(full_path)
                folder_timestamps[full_path] = (stat.st_atime, stat.st_mtime)
            except:
                pass

    for root, dirs, files in os.walk(".", topdown=True):

        if is_in_excluded_path(root):
            dirs[:] = []
            continue

        dirs[:] = [
            d for d in dirs
            if not is_in_excluded_path(os.path.join(root, d))
            and not should_exclude(d)
            and d not in RUNTIME_EXCLUDED_NAMES
        ]

        all_items = dirs + files

        for item in all_items:
            full_path = os.path.abspath(os.path.join(root, item))

            if item == PREVIEW_FILE:
                continue

            if is_in_excluded_path(full_path):
                skip_list.append(f"{full_path} (EXCLUDED PATH)")
                continue

            if item in RUNTIME_EXCLUDED_NAMES:
                seen_cli_items.add(item)
                skip_list.append(f"{full_path} (CLI PARAMETER)")
                continue

            if not os.path.exists(full_path):
                continue

            if should_exclude(item):
                skip_list.append(f"{full_path} (SYSTEM EXCLUSION)")
                continue

            depth = get_depth(full_path)
            if MAX_DEPTH != 0 and depth > MAX_DEPTH:
                skip_list.append(f"{full_path} (MAX DEPTH EXCEEDED)")
                continue

            new_name = transform_name(item)
            new_full_path = os.path.abspath(os.path.join(root, new_name))

            if new_name == item:
                keep_list.append(full_path)
            else:
                rename_list.append((full_path, new_full_path))

                # track folder renames
                if os.path.isdir(full_path):
                    folder_renames[full_path] = new_full_path

    rename_list.sort(key=lambda x: x[0].count(os.sep), reverse=True)

    # =========================
    # PREVIEW
    # =========================
    if DRY_RUN:
        with open(PREVIEW_FILE, "w", encoding="utf-8") as f:
            f.write("RENAME PREVIEW (DRY RUN)\n")
            f.write("========================\n\n")

            # =========================
            # RENAME
            # =========================
            f.write("RENAME:\n")
            f.write("--------\n")
            for old, new in rename_list:
                if HIDE_FOLDERS_FROM_PREVIEW:
                    f.write(f"{os.path.basename(old)} -> {os.path.basename(new)}\n")
                else:
                    f.write(f"{old} -> {new}\n")

            # =========================
            # KEEP
            # =========================
            f.write("\nKEEP (UNCHANGED):\n")
            f.write("------------------\n")
            for k in keep_list:
                if HIDE_FOLDERS_FROM_PREVIEW:
                    f.write(f"{os.path.basename(k)}\n")
                else:
                    f.write(f"{k}\n")

            # =========================
            # SKIP
            # =========================
            f.write("\nSKIP (EXCLUDED / IGNORED):\n")
            f.write("--------------------------\n")
            for s in skip_list:
                if HIDE_FOLDERS_FROM_PREVIEW:
                    # Extract just the name + reason
                    name = os.path.basename(s.split(" (")[0])
                    reason = s[s.find(" ("):]
                    f.write(f"{name}{reason}\n")
                else:
                    f.write(f"{s}\n")

            # =========================
            # SUMMARY
            # =========================
            renamed_files = 0
            renamed_folders = 0

            for old, _ in rename_list:
                if os.path.isdir(old):
                    renamed_folders += 1
                else:
                    renamed_files += 1

            kept_files = 0
            kept_folders = 0

            for k in keep_list:
                if os.path.isdir(k):
                    kept_folders += 1
                else:
                    kept_files += 1

            skipped_files = 0
            skipped_folders = 0

            for s in skip_list:
                path = s.split(" (")[0]  # remove reason
                if os.path.isdir(path):
                    skipped_folders += 1
                else:
                    skipped_files += 1

            f.write("\nSUMMARY:\n")
            f.write("--------\n")
            f.write(f"Total Renamed : {len(rename_list)}\n")
            f.write(f"  Files       : {renamed_files}\n")
            f.write(f"  Folders     : {renamed_folders}\n\n")

            f.write(f"Total Kept    : {len(keep_list)}\n")
            f.write(f"  Files       : {kept_files}\n")
            f.write(f"  Folders     : {kept_folders}\n\n")

            f.write(f"Total Skipped : {len(skip_list)}\n")
            f.write(f"  Files       : {skipped_files}\n")
            f.write(f"  Folders     : {skipped_folders}\n")

        print(f"Dry run complete. Preview written to {PREVIEW_FILE}")
        return


    # =========================
    # EXECUTE
    # =========================
    for old, new in rename_list:
        try:
            src_stat = os.stat(old)
            os.rename(old, new)

            if os.path.exists(new):
                preserve_metadata(new, src_stat)

            print(f"Renamed: {old} -> {new}")

        except Exception as e:
            print(f"[ERROR] {old} -> {e}")

    # =========================
    # RESTORE FOLDER TIMESTAMPS
    # =========================
    for old_path, (atime, mtime) in folder_timestamps.items():
        new_path = folder_renames.get(old_path, old_path)

        if os.path.exists(new_path):
            try:
                os.utime(new_path, (atime, mtime))
            except:
                pass

    print("Renaming complete.")

# =========================
# RUN
# =========================
if __name__ == "__main__":
    main() 