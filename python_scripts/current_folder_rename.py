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

# =========================
# INCLUDED ACRONYMS
# =========================
INCLUDED_ACRONYMS = "api http https json xml sql jwt pdf csv html css ip tcp udp db id ui url ssl"
INCLUDED_ACRONYMS = set(INCLUDED_ACRONYMS.split())

INCLUDED_ACRONYMS = {a.lower() for a in INCLUDED_ACRONYMS}

# =========================
# PARSE CLI FLAGS
# =========================
args = {arg.lower() for arg in sys.argv[1:]}

if "dry-run-false" in args:
    DRY_RUN = False

RUNTIME_EXCLUDED_NAMES = {
    arg for arg in sys.argv[1:]
    if arg.lower() != "dry-run-false"
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

    words = base.split("-")

    small_words = {
        "a", "an", "the", "and", "but", "or", "nor", "for",
        "so", "yet", "as", "at", "by", "in", "of", "on",
        "to", "up", "with", "from", "into", "onto", "over",
        "under", "between", "without", "within"
    }

    transformed = []

    for i, word in enumerate(words):
        if not word:
            continue

        lower = word.lower()

        # =========================
        # ACRONYM HANDLING (NEW)
        # =========================
        if lower in INCLUDED_ACRONYMS:
            transformed.append(lower.upper())
            continue

        if i == 0:
            transformed.append(lower.capitalize())
        elif lower in small_words:
            transformed.append(lower)
        else:
            transformed.append(lower.capitalize())

    return f"{'-'.join(transformed)}{ext}"

# =========================
# METADATA PRESERVATION
# =========================
def preserve_metadata(dst, src_stat):
    os.utime(dst, (src_stat.st_atime, src_stat.st_mtime))

    if os.name == "nt":
        FILE_WRITE_ATTRIBUTES = 0x100

        CreateFile = ctypes.windll.kernel32.CreateFileW
        SetFileTime = ctypes.windll.kernel32.SetFileTime
        CloseHandle = ctypes.windll.kernel32.CloseHandle

        class FILETIME(ctypes.Structure):
            _fields_ = [
                ("dwLowDateTime", wintypes.DWORD),
                ("dwHighDateTime", wintypes.DWORD)
            ]

        def to_filetime(timestamp):
            ft = int((timestamp + 11644473600) * 10000000)
            return FILETIME(ft & 0xFFFFFFFF, ft >> 32)

        handle = CreateFile(dst, FILE_WRITE_ATTRIBUTES, 0, None, 3, 0, None)

        if handle != -1:
            ctime = to_filetime(src_stat.st_ctime)
            atime = to_filetime(src_stat.st_atime)
            mtime = to_filetime(src_stat.st_mtime)

            SetFileTime(handle,
                        ctypes.byref(ctime),
                        ctypes.byref(atime),
                        ctypes.byref(mtime))

            CloseHandle(handle)

# =========================
# MAIN
# =========================
def main():
    items = os.listdir(".")

    rename_list = []
    keep_list = []
    skip_list = []

    seen_cli_items = set()

    for item in items:
        if item == PREVIEW_FILE:
            continue

        if item in RUNTIME_EXCLUDED_NAMES:
            seen_cli_items.add(item)
            skip_list.append(f"{item} (CLI PARAMETER)")
            continue

        if should_exclude(item):
            skip_list.append(f"{item} (SYSTEM EXCLUSION)")
            continue

        new_name = transform_name(item)

        if new_name == item:
            keep_list.append(item)
        else:
            rename_list.append((item, new_name))

    missing = RUNTIME_EXCLUDED_NAMES - seen_cli_items
    for m in missing:
        skip_list.append(f"{m} (NOT FOUND)")

    rename_list.sort(key=lambda x: x[0])
    keep_list.sort()
    skip_list.sort()

    # =========================
    # DRY RUN OUTPUT
    # =========================
    if DRY_RUN:
        with open(PREVIEW_FILE, "w", encoding="utf-8") as f:
            f.write("RENAME PREVIEW (DRY RUN)\n")
            f.write("========================\n\n")

            f.write("RENAME:\n")
            for old, new in rename_list:
                f.write(f"{old} -> {new}\n")

            f.write("\nKEEP (Already correctly formatted):\n")
            for k in keep_list:
                f.write(f"{k}\n")

            f.write("\nSKIP:\n")
            for s in skip_list:
                f.write(f"{s}\n")

        print(f"Dry run complete. Preview written to {PREVIEW_FILE}")
        return

    # =========================
    # EXECUTE RENAME
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

    print("Renaming complete.") 

# =========================
# RUN
# =========================
if __name__ == "__main__":
    main()