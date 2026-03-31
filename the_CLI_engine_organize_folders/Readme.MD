# FileOrganizer — Complete Toolkit

Automatically organize messy folders by file type.  
Three ways to use it: **CLI**, **config file**, and a **GUI app**.

---

## 📁 Files

| File | What it does |

|---|---|
| `organize.py` | Core engine + full CLI tool |
| `gui.py` | Desktop GUI app (Tkinter, no install needed) |
| `organizer_config.json` | Starter config — edit and use with `--config` |

---

## 🚀 Quick Start

### Install (no pip needed — stdlib only)

```bash
# Make the CLI globally available (macOS / Linux)
chmod +x organize.py
sudo ln -s "$(pwd)/organize.py" /usr/local/bin/organize
```

### Launch the GUI

```bash
python gui.py
```

---

## 💻 CLI Usage

```bash
# Basic — organize a folder
organize ~/Downloads

# Dry-run — preview only, nothing moves
organize ~/Downloads --dry-run

# Watch mode — auto-organize as new files arrive
organize ~/Downloads --watch

# Use a custom mapping config
organize ~/Downloads --config organizer_config.json

# Generate a starter config to customise
organize --init-config
```

---

## ⚙️ Config File

Edit `organizer_config.json` to define your own categories:

```json
{
  "Design":    [".fig", ".sketch", ".xd", ".psd", ".ai"],
  "Images":    [".jpg", ".png", ".webp"],
  "Documents": [".pdf", ".docx", ".md"]
}
```

Then use it:

```bash
organize ~/Downloads --config organizer_config.json
```

Files with extensions not in any category go to an **Others/** folder.

---

## 🛡️ Safety Features

| Risk | Protection |

|---|---|
| Overwriting files | Appends `_1`, `_2`… to avoid collisions |
| Moving directories | Only moves files (`os.path.isfile` check) |
| Moving the script | Detected via `__file__` and skipped |
| Missing destination | Created automatically (`os.makedirs`) |

---

## 🔧 How the Core Functions Work

### `os.listdir(path)`

Returns a **flat list** of names in the directory — files and folders alike, no recursion, no `.` or `..`. The script filters out directories afterward with `os.path.isfile()`.

### `shutil.move(src, dst)`

Tries `os.rename()` first (instant, same filesystem). If source and destination are on different disks, it falls back to copy-then-delete — so data is never lost mid-move.

---

## 📦 Default Categories

| Folder | Extensions |

|---|---|
| Images | jpg, jpeg, png, gif, bmp, svg, webp, tiff, ico, heic, raw |
| Documents | pdf, doc, docx, txt, xls, xlsx, ppt, pptx, odt, csv, rtf, md |
| Videos | mp4, mov, avi, mkv, flv, wmv, webm, m4v, mpeg, 3gp |
| Audio | mp3, wav, aac, flac, ogg, wma, m4a, aiff, opus |
| Archives | zip, rar, tar, gz, 7z, bz2, xz, iso |
| Code | py, js, ts, html, css, java, c, cpp, json, yml, sh, sql… |
| Executables | exe, msi, dmg, pkg, apk, deb, rpm |
| Fonts | ttf, otf, woff, woff2 |
| eBooks | epub, mobi, azw3 |
| Torrents | torrent |
| Others | *(anything not matched above)* |
