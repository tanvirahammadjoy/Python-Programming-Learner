#!/usr/bin/env python3
"""
╔══════════════════════════════════════════╗
║         F I L E O R G A N I Z E R       ║
║  CLI · Config · Dry-run · Live Watcher  ║
╚══════════════════════════════════════════╝

Usage:
    organize <path>                  Organize the directory
    organize <path> --dry-run        Preview only, nothing moves
    organize <path> --watch          Watch & auto-organize new files
    organize <path> --config cfg.json  Use a custom mapping config
    organize --init-config           Create a starter config file
"""

import os
import sys
import json
import shutil
import argparse
import time
import threading
from datetime import datetime
from pathlib import Path


# ─────────────────────────────────────────────────────────────
#  DEFAULTS  (used when no config file is provided)
# ─────────────────────────────────────────────────────────────

DEFAULT_MAPPING: dict[str, list[str]] = {
    "Images":      [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg",
                    ".webp", ".tiff", ".ico", ".heic", ".raw"],
    "Documents":   [".pdf", ".doc", ".docx", ".txt", ".xls", ".xlsx",
                    ".ppt", ".pptx", ".odt", ".csv", ".rtf", ".md",
                    ".pages", ".numbers", ".key"],
    "Videos":      [".mp4", ".mov", ".avi", ".mkv", ".flv", ".wmv",
                    ".webm", ".m4v", ".mpeg", ".3gp"],
    "Audio":       [".mp3", ".wav", ".aac", ".flac", ".ogg", ".wma",
                    ".m4a", ".aiff", ".opus"],
    "Archives":    [".zip", ".rar", ".tar", ".gz", ".7z", ".bz2",
                    ".xz", ".iso", ".tar.gz", ".tgz"],
    "Code":        [".py", ".js", ".ts", ".html", ".css", ".java",
                    ".c", ".cpp", ".h", ".json", ".xml", ".yml",
                    ".yaml", ".sh", ".bat", ".sql", ".php", ".rb",
                    ".go", ".rs", ".swift", ".kt", ".dart"],
    "Executables": [".exe", ".msi", ".dmg", ".pkg", ".apk", ".deb", ".rpm"],
    "Fonts":       [".ttf", ".otf", ".woff", ".woff2"],
    "eBooks":      [".epub", ".mobi", ".azw3"],
    "Torrents":    [".torrent"],
}

STARTER_CONFIG = {
    "_comment": "Customize folder names and extensions. Files with unknown extensions go to 'Others'.",
    "Images":    [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"],
    "Documents": [".pdf", ".docx", ".txt", ".xlsx", ".pptx", ".csv", ".md"],
    "Videos":    [".mp4", ".mov", ".avi", ".mkv"],
    "Audio":     [".mp3", ".wav", ".flac", ".aac"],
    "Archives":  [".zip", ".rar", ".7z", ".tar.gz"],
    "Code":      [".py", ".js", ".html", ".css", ".json", ".sh"],
}


# ─────────────────────────────────────────────────────────────
#  ANSI COLOURS  (skipped on Windows if not supported)
# ─────────────────────────────────────────────────────────────

class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    DIM    = "\033[2m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    CYAN   = "\033[96m"
    RED    = "\033[91m"
    BLUE   = "\033[94m"
    MAGENTA= "\033[95m"
    WHITE  = "\033[97m"

def _no_color():
    """Disable colors (e.g., when piped to a file)."""
    for attr in vars(C):
        if not attr.startswith("_"):
            setattr(C, attr, "")

if not sys.stdout.isatty():
    _no_color()


# ─────────────────────────────────────────────────────────────
#  LOGGER  – pretty, timestamped output
# ─────────────────────────────────────────────────────────────

class Logger:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.moved   = 0
        self.skipped = 0
        self.errors  = 0
        self._lock   = threading.Lock()

    def _ts(self) -> str:
        return f"{C.DIM}{datetime.now().strftime('%H:%M:%S')}{C.RESET}"

    def moved_file(self, src: str, dest_folder: str, renamed_to: str = ""):
        with self._lock:
            self.moved += 1
            tag  = f"{C.YELLOW}[DRY-RUN]{C.RESET}" if self.dry_run else f"{C.GREEN}[MOVED]{C.RESET}  "
            name = f"{C.WHITE}{src}{C.RESET}"
            dest = f"{C.CYAN}{dest_folder}/{C.RESET}"
            ren  = f" {C.DIM}→ renamed '{renamed_to}'{C.RESET}" if renamed_to else ""
            print(f"  {self._ts()} {tag} {name} → {dest}{ren}")

    def skipped_file(self, name: str, reason: str):
        with self._lock:
            self.skipped += 1
            print(f"  {self._ts()} {C.DIM}[SKIP]    {name} ({reason}){C.RESET}")

    def error(self, name: str, err: str):
        with self._lock:
            self.errors += 1
            print(f"  {self._ts()} {C.RED}[ERROR]   {name}: {err}{C.RESET}")

    def watching(self, name: str):
        with self._lock:
            print(f"  {self._ts()} {C.MAGENTA}[WATCH]   New file detected: {C.WHITE}{name}{C.RESET}")

    def summary(self):
        mode = f"{C.YELLOW} (DRY-RUN — nothing was moved){C.RESET}" if self.dry_run else ""
        print(f"\n{C.BOLD}{'─'*54}{C.RESET}")
        print(f"  {C.GREEN}✔  Moved   : {self.moved}{C.RESET}   "
              f"{C.DIM}Skipped: {self.skipped}   "
              f"{C.RED if self.errors else C.DIM}Errors: {self.errors}{C.RESET}{mode}")
        print(f"{C.BOLD}{'─'*54}{C.RESET}\n")


# ─────────────────────────────────────────────────────────────
#  CONFIG  – load from JSON or fall back to defaults
# ─────────────────────────────────────────────────────────────

def load_mapping(config_path: str | None) -> dict[str, list[str]]:
    """Return extension→folder mapping from a JSON file or built-in defaults."""
    if config_path is None:
        return DEFAULT_MAPPING

    path = Path(config_path)
    if not path.exists():
        print(f"{C.RED}[ERROR] Config file not found: {config_path}{C.RESET}")
        sys.exit(1)

    with open(path, "r") as f:
        raw = json.load(f)

    # Strip comment keys
    mapping = {k: v for k, v in raw.items() if not k.startswith("_")}
    print(f"{C.CYAN}[CONFIG] Loaded mapping from {config_path} "
          f"({len(mapping)} categories){C.RESET}\n")
    return mapping


def build_ext_index(mapping: dict[str, list[str]]) -> dict[str, str]:
    """Build a reverse lookup: '.jpg' → 'Images'."""
    return {
        ext.lower(): folder
        for folder, exts in mapping.items()
        for ext in exts
    }


def init_config(dest: str = "organizer_config.json"):
    """Write a starter config file the user can customise."""
    path = Path(dest)
    if path.exists():
        print(f"{C.YELLOW}File already exists: {dest}{C.RESET}")
        return
    with open(path, "w") as f:
        json.dump(STARTER_CONFIG, f, indent=2)
    print(f"{C.GREEN}✔  Starter config written to {dest}{C.RESET}")
    print(f"  Edit it, then run: {C.CYAN}organize <path> --config {dest}{C.RESET}")


# ─────────────────────────────────────────────────────────────
#  CORE LOGIC  – move (or preview) a single file
# ─────────────────────────────────────────────────────────────

def process_file(
    item_name: str,
    directory: Path,
    ext_index: dict[str, str],
    script_name: str,
    log: Logger,
    dry_run: bool,
) -> None:
    item_path = directory / item_name

    # Skip directories
    if not item_path.is_file():
        log.skipped_file(item_name, "directory")
        return

    # Skip this script
    if item_name == script_name:
        log.skipped_file(item_name, "this is the organizer script")
        return

    # Determine extension
    _, ext = os.path.splitext(item_name)
    ext = ext.lower()

    folder_name = ext_index.get(ext, "Others")
    dest_folder = directory / folder_name

    # Skip files already inside a managed sub-folder
    # (only relevant during --watch when the folder itself is the root)
    if item_path.parent != directory:
        log.skipped_file(item_name, "already in sub-folder")
        return

    dest_file = dest_folder / item_name

    # Resolve name collision
    renamed_to = ""
    if dest_file.exists():
        base, e = os.path.splitext(item_name)
        counter = 1
        while dest_file.exists():
            new_name = f"{base}_{counter}{e}"
            dest_file = dest_folder / new_name
            counter += 1
        renamed_to = dest_file.name

    if not dry_run:
        try:
            dest_folder.mkdir(parents=True, exist_ok=True)
            shutil.move(str(item_path), str(dest_file))
        except Exception as err:
            log.error(item_name, str(err))
            return

    log.moved_file(item_name, folder_name, renamed_to)


# ─────────────────────────────────────────────────────────────
#  ONE-SHOT ORGANISE
# ─────────────────────────────────────────────────────────────

def organize(directory: str, ext_index: dict[str, str], log: Logger, dry_run: bool):
    path = Path(directory).expanduser().resolve()

    if not path.exists():
        print(f"{C.RED}[ERROR] Directory not found: {path}{C.RESET}")
        sys.exit(1)

    script_name = Path(__file__).name
    mode_label  = f"{C.YELLOW}DRY-RUN{C.RESET}" if dry_run else f"{C.GREEN}LIVE{C.RESET}"

    print(f"\n{C.BOLD}{'═'*54}{C.RESET}")
    print(f"  {C.BOLD}FileOrganizer{C.RESET}  •  mode: {mode_label}")
    print(f"  {C.DIM}Target:{C.RESET} {path}")
    print(f"{C.BOLD}{'═'*54}{C.RESET}\n")

    # os.listdir() — flat list of names in the directory
    for item_name in sorted(os.listdir(path)):
        process_file(item_name, path, ext_index, script_name, log, dry_run)

    log.summary()


# ─────────────────────────────────────────────────────────────
#  WATCHER  – polls the directory every 2 s for new files
# ─────────────────────────────────────────────────────────────

def watch(directory: str, ext_index: dict[str, str], log: Logger):
    path = Path(directory).expanduser().resolve()

    if not path.exists():
        print(f"{C.RED}[ERROR] Directory not found: {path}{C.RESET}")
        sys.exit(1)

    script_name = Path(__file__).name

    print(f"\n{C.BOLD}{'═'*54}{C.RESET}")
    print(f"  {C.BOLD}FileOrganizer{C.RESET}  •  mode: {C.MAGENTA}WATCHER{C.RESET}")
    print(f"  {C.DIM}Target:{C.RESET} {path}")
    print(f"  {C.DIM}Polling every 2 s — press Ctrl+C to stop{C.RESET}")
    print(f"{C.BOLD}{'═'*54}{C.RESET}\n")

    # First, organise whatever is already there
    for item_name in sorted(os.listdir(path)):
        process_file(item_name, path, ext_index, script_name, log, dry_run=False)

    # Build a snapshot of known files so we only react to NEW arrivals
    known: set[str] = set(os.listdir(path))

    print(f"\n  {C.MAGENTA}Watching for new files…{C.RESET}\n")

    try:
        while True:
            time.sleep(2)
            current = set(os.listdir(path))
            new_files = current - known

            for item_name in sorted(new_files):
                item_path = path / item_name
                # Brief pause so the file is fully written before we move it
                time.sleep(0.5)
                log.watching(item_name)
                process_file(item_name, path, ext_index, script_name, log, dry_run=False)

            known = set(os.listdir(path))

    except KeyboardInterrupt:
        print(f"\n  {C.CYAN}Watcher stopped.{C.RESET}")
        log.summary()


# ─────────────────────────────────────────────────────────────
#  CLI  – argument parsing
# ─────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="organize",
        description="Automatically organize a messy directory by file type.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  organize ~/Downloads
  organize ~/Desktop --dry-run
  organize ~/Downloads --watch
  organize ~/Downloads --config my_mapping.json
  organize --init-config
        """,
    )

    parser.add_argument(
        "directory",
        nargs="?",
        help="Path to the directory to organize (omit with --init-config)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview moves without actually moving any files",
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Watch the directory and organize new files as they appear",
    )
    parser.add_argument(
        "--config",
        metavar="FILE",
        help="Path to a JSON config file defining the folder→extension mapping",
    )
    parser.add_argument(
        "--init-config",
        action="store_true",
        help="Write a starter config file (organizer_config.json) and exit",
    )
    return parser


def main():
    parser = build_parser()
    args   = parser.parse_args()

    # ── --init-config ──────────────────────────────────────────
    if args.init_config:
        init_config()
        return

    # ── Require directory for all other modes ──────────────────
    if not args.directory:
        parser.print_help()
        sys.exit(0)

    mapping   = load_mapping(args.config)
    ext_index = build_ext_index(mapping)
    log       = Logger(dry_run=args.dry_run)

    if args.watch:
        if args.dry_run:
            print(f"{C.YELLOW}[WARN] --dry-run is ignored in --watch mode.{C.RESET}")
        watch(args.directory, ext_index, log)
    else:
        organize(args.directory, ext_index, log, dry_run=args.dry_run)


if __name__ == "__main__":
    main()