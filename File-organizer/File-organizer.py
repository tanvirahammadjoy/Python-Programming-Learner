"""
File Organizer Script
Automatically organizes files in a directory by their extension.
"""

import os
import shutil

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────

# Set the path to the folder you want to organize.
# Change this to your actual target directory, e.g.:
# DIRECTORY_TO_ORGANIZE = "/Users/yourname/Downloads"
DIRECTORY_TO_ORGANIZE = os.path.expanduser("~/Downloads")

# Dictionary mapping folder names → lists of file extensions.
# Add or remove entries here to customise your own categories.
FOLDER_MAPPING = {
    "Images":     [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg",
                   ".webp", ".tiff", ".ico", ".heic"],
    "Documents":  [".pdf", ".doc", ".docx", ".txt", ".xls", ".xlsx",
                   ".ppt", ".pptx", ".odt", ".csv", ".rtf", ".md"],
    "Videos":     [".mp4", ".mov", ".avi", ".mkv", ".flv", ".wmv",
                   ".webm", ".m4v", ".mpeg"],
    "Audio":      [".mp3", ".wav", ".aac", ".flac", ".ogg", ".wma",
                   ".m4a", ".aiff"],
    "Archives":   [".zip", ".rar", ".tar", ".gz", ".7z", ".bz2",
                   ".xz", ".iso"],
    "Code":       [".py", ".js", ".ts", ".html", ".css", ".java",
                   ".c", ".cpp", ".h", ".json", ".xml", ".yml",
                   ".yaml", ".sh", ".bat", ".sql", ".php", ".rb"],
    "Executables":[".exe", ".msi", ".dmg", ".pkg", ".apk", ".deb",
                   ".rpm"],
    "Fonts":      [".ttf", ".otf", ".woff", ".woff2"],
    "Torrents":   [".torrent"],
}

# ─────────────────────────────────────────────
# HELPER: build a reverse lookup  extension → folder
# ─────────────────────────────────────────────
# Example result: {".jpg": "Images", ".pdf": "Documents", ...}
EXTENSION_TO_FOLDER = {
    ext: folder
    for folder, extensions in FOLDER_MAPPING.items()
    for ext in extensions
}

# ─────────────────────────────────────────────
# MAIN ORGANISER FUNCTION
# ─────────────────────────────────────────────

def organize_directory(directory: str) -> None:
    """
    Walk through every item in `directory` and move files
    into the appropriate sub-folder based on their extension.
    """

    # Resolve the absolute path so relative paths work correctly.
    directory = os.path.abspath(directory)

    # Safety check – make sure the target directory actually exists.
    if not os.path.exists(directory):
        print(f"[ERROR] Directory not found: {directory}")
        return

    # Get the filename of THIS script so we can skip it later.
    # __file__ is a built-in Python variable that holds the path
    # of the currently running script.
    script_name = os.path.basename(__file__)

    # ── os.listdir() ──────────────────────────────────────────────
    # Returns a plain Python list of every name (files AND folders)
    # inside `directory`.  It does NOT recurse into sub-folders and
    # does NOT include "." or "..".
    # Example: ["photo.jpg", "report.pdf", "old_folder", "song.mp3"]
    all_items = os.listdir(directory)

    moved_count = 0
    skipped_count = 0

    for item_name in all_items:

        # Build the full path so os/shutil functions can locate the item.
        item_path = os.path.join(directory, item_name)

        # ── Safety check 1: skip directories ──────────────────────
        # os.path.isfile() returns True only for regular files,
        # so folders, symlinks-to-folders, etc. are ignored.
        if not os.path.isfile(item_path):
            print(f"  [SKIP] '{item_name}' is a directory – leaving it alone.")
            skipped_count += 1
            continue

        # ── Safety check 2: never move the script itself ──────────
        if item_name == script_name:
            print(f"  [SKIP] '{item_name}' is this script – leaving it alone.")
            skipped_count += 1
            continue

        # ── Determine the file's extension ────────────────────────
        # os.path.splitext("photo.jpg")  →  ("photo", ".jpg")
        # We use .lower() so ".JPG" and ".jpg" match the same entry.
        _, extension = os.path.splitext(item_name)
        extension = extension.lower()

        # Look up which folder this extension belongs to.
        # If the extension isn't in our mapping, put it in "Others".
        destination_folder_name = EXTENSION_TO_FOLDER.get(extension, "Others")
        destination_folder_path = os.path.join(directory, destination_folder_name)

        # ── Safety check 3: create the destination if needed ──────
        # os.makedirs() creates the full path of directories.
        # exist_ok=True means it won't raise an error if the folder
        # already exists.
        os.makedirs(destination_folder_path, exist_ok=True)

        # Build the full destination path for this specific file.
        destination_file_path = os.path.join(destination_folder_path, item_name)

        # ── Handle filename collisions ─────────────────────────────
        # If a file with the same name already exists in the target
        # folder, append a counter to avoid overwriting it.
        if os.path.exists(destination_file_path):
            base, ext = os.path.splitext(item_name)
            counter = 1
            while os.path.exists(destination_file_path):
                new_name = f"{base}_{counter}{ext}"
                destination_file_path = os.path.join(
                    destination_folder_path, new_name
                )
                counter += 1

        # ── shutil.move() ──────────────────────────────────────────
        # Moves `item_path` to `destination_file_path`.
        # Under the hood it tries os.rename() first (fast, same
        # filesystem); if that fails (e.g., cross-device) it falls
        # back to copy-then-delete so no data is ever lost.
        shutil.move(item_path, destination_file_path)

        moved_name = os.path.basename(destination_file_path)
        print(f"  [MOVED] '{item_name}' → '{destination_folder_name}/' "
              + (f"(renamed to '{moved_name}')"
                 if moved_name != item_name else ""))
        moved_count += 1

    # ── Summary ───────────────────────────────────────────────────
    print("\n" + "─" * 50)
    print(f"  Done! Files moved: {moved_count} | Skipped: {skipped_count}")
    print("─" * 50)


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print(f"\nOrganising: {DIRECTORY_TO_ORGANIZE}\n" + "─" * 50)
    organize_directory(DIRECTORY_TO_ORGANIZE)