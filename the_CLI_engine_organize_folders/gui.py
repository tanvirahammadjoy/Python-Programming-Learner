#!/usr/bin/env python3
"""
FileOrganizer GUI — powered by Tkinter (stdlib, no pip install needed).
Run:  python gui.py
"""

import os
import sys
import json
import shutil
import threading
import time
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

# ── Re-use core logic from organize.py (same directory) ──────────────────────
sys.path.insert(0, str(Path(__file__).parent))
from organize import DEFAULT_MAPPING, build_ext_index, Logger


# ─────────────────────────────────────────────────────────────
#  COLOURS & THEME
# ─────────────────────────────────────────────────────────────

BG        = "#0f1117"   # near-black background
PANEL     = "#1a1d27"   # card / panel
BORDER    = "#2a2d3a"   # subtle border
ACCENT    = "#6c63ff"   # purple accent
ACCENT2   = "#00d4aa"   # teal / green
WARN      = "#f5a623"   # amber
ERR       = "#ff5c5c"   # red
FG        = "#e8eaf0"   # primary text
FG_DIM    = "#6b7280"   # muted text
SUCCESS   = "#4ade80"   # moved files
FONT_MONO = ("Consolas", "Courier New", "monospace")


# ─────────────────────────────────────────────────────────────
#  GUI LOGGER  (feeds the log panel inside the app)
# ─────────────────────────────────────────────────────────────

class GUILogger(Logger):
    def __init__(self, log_widget: scrolledtext.ScrolledText, stats_cb, dry_run=False):
        super().__init__(dry_run=dry_run)
        self.log   = log_widget
        self._cb   = stats_cb   # called after every event to refresh counters

    def _write(self, text: str, tag: str = "normal"):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log.configure(state="normal")
        self.log.insert("end", f"[{ts}]  ", "dim")
        self.log.insert("end", text + "\n", tag)
        self.log.see("end")
        self.log.configure(state="disabled")
        self._cb(self.moved, self.skipped, self.errors)

    def moved_file(self, src, dest_folder, renamed_to=""):
        with self._lock:
            self.moved += 1
            prefix = "DRY-RUN" if self.dry_run else "MOVED"
            tag    = "warn"    if self.dry_run else "ok"
            ren    = f"  (→ {renamed_to})" if renamed_to else ""
            self._write(f"[{prefix}]  {src}  →  {dest_folder}/{ren}", tag)

    def skipped_file(self, name, reason):
        with self._lock:
            self.skipped += 1
            self._write(f"[SKIP]   {name}  ({reason})", "dim")

    def error(self, name, err):
        with self._lock:
            self.errors += 1
            self._write(f"[ERROR]  {name}: {err}", "err")

    def watching(self, name):
        with self._lock:
            self._write(f"[WATCH]  New file detected: {name}", "watch")

    def summary(self):
        with self._lock:
            mode = " (DRY-RUN)" if self.dry_run else ""
            self._write(
                f"{'─'*42}  Done{mode}  "
                f"Moved:{self.moved}  Skipped:{self.skipped}  Errors:{self.errors}",
                "summary",
            )


# ─────────────────────────────────────────────────────────────
#  MAIN APP WINDOW
# ─────────────────────────────────────────────────────────────

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FileOrganizer")
        self.geometry("820x640")
        self.minsize(680, 520)
        self.configure(bg=BG)

        self._watching   = False
        self._watch_stop = threading.Event()
        self._mapping    = DEFAULT_MAPPING.copy()

        self._build_ui()
        self._apply_log_tags()

    # ── UI construction ─────────────────────────────────────────

    def _build_ui(self):
        # ── Top bar ─────────────────────────────────────────────
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=20, pady=(18, 0))

        tk.Label(top, text="FileOrganizer", font=("Georgia", 22, "bold"),
                 fg=ACCENT, bg=BG).pack(side="left")
        tk.Label(top, text="  clean your mess in one click",
                 font=("Georgia", 11, "italic"), fg=FG_DIM, bg=BG).pack(side="left")

        # ── Directory picker ────────────────────────────────────
        pick_frame = tk.Frame(self, bg=PANEL, bd=0, highlightthickness=1,
                               highlightbackground=BORDER)
        pick_frame.pack(fill="x", padx=20, pady=14)

        tk.Label(pick_frame, text="Directory", font=("Georgia", 9),
                 fg=FG_DIM, bg=PANEL).pack(anchor="w", padx=12, pady=(10, 0))

        row = tk.Frame(pick_frame, bg=PANEL)
        row.pack(fill="x", padx=12, pady=(4, 10))

        self._dir_var = tk.StringVar()
        entry = tk.Entry(row, textvariable=self._dir_var, font=("Consolas", 11),
                         bg="#252836", fg=FG, insertbackground=FG,
                         relief="flat", bd=0)
        entry.pack(side="left", fill="x", expand=True, ipady=6, ipadx=6)

        tk.Button(row, text="Browse…", font=("Georgia", 10),
                  bg=ACCENT, fg="white", relief="flat", bd=0, cursor="hand2",
                  activebackground="#554ccc", activeforeground="white",
                  command=self._browse, padx=12, pady=5).pack(side="right", padx=(8, 0))

        # ── Options row ─────────────────────────────────────────
        opt = tk.Frame(self, bg=BG)
        opt.pack(fill="x", padx=20, pady=(0, 8))

        self._dry_run_var = tk.BooleanVar()
        self._watch_var   = tk.BooleanVar()

        for text, var, color in [
            ("🔍 Dry-run (preview only)", self._dry_run_var, WARN),
            ("👁  Watch mode (auto-organize)",  self._watch_var,   ACCENT2),
        ]:
            cb = tk.Checkbutton(opt, text=text, variable=var,
                                font=("Georgia", 10), fg=color, bg=BG,
                                activebackground=BG, activeforeground=color,
                                selectcolor="#1a1d27", bd=0, cursor="hand2")
            cb.pack(side="left", padx=(0, 20))

        # ── Config button ────────────────────────────────────────
        tk.Button(opt, text="⚙  Load Config…", font=("Georgia", 10),
                  bg=PANEL, fg=FG_DIM, relief="flat", bd=0, cursor="hand2",
                  activebackground=BORDER, activeforeground=FG,
                  command=self._load_config, padx=10).pack(side="right")

        # ── Action buttons ───────────────────────────────────────
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(fill="x", padx=20, pady=(0, 12))

        self._run_btn = tk.Button(
            btn_row, text="▶  Organize Now", font=("Georgia", 12, "bold"),
            bg=ACCENT, fg="white", relief="flat", bd=0, cursor="hand2",
            activebackground="#554ccc", activeforeground="white",
            command=self._run, padx=20, pady=8)
        self._run_btn.pack(side="left")

        self._stop_btn = tk.Button(
            btn_row, text="■  Stop Watcher", font=("Georgia", 12, "bold"),
            bg=ERR, fg="white", relief="flat", bd=0, cursor="hand2",
            activebackground="#cc4444", activeforeground="white",
            command=self._stop_watch, padx=20, pady=8, state="disabled")
        self._stop_btn.pack(side="left", padx=(10, 0))

        tk.Button(btn_row, text="🗑  Clear Log", font=("Georgia", 10),
                  bg=PANEL, fg=FG_DIM, relief="flat", bd=0, cursor="hand2",
                  activebackground=BORDER, activeforeground=FG,
                  command=self._clear_log, padx=12, pady=8).pack(side="right")

        # ── Stats bar ───────────────────────────────────────────
        stats = tk.Frame(self, bg=PANEL, bd=0, highlightthickness=1,
                          highlightbackground=BORDER)
        stats.pack(fill="x", padx=20, pady=(0, 8))

        self._stat_labels = {}
        for key, label, color in [
            ("moved",   "Moved",   SUCCESS),
            ("skipped", "Skipped", FG_DIM),
            ("errors",  "Errors",  ERR),
        ]:
            f = tk.Frame(stats, bg=PANEL)
            f.pack(side="left", padx=20, pady=8)
            tk.Label(f, text=label, font=("Georgia", 9), fg=FG_DIM, bg=PANEL).pack()
            lbl = tk.Label(f, text="0", font=("Georgia", 18, "bold"), fg=color, bg=PANEL)
            lbl.pack()
            self._stat_labels[key] = lbl

        self._status_lbl = tk.Label(stats, text="Ready", font=("Georgia", 10, "italic"),
                                     fg=FG_DIM, bg=PANEL)
        self._status_lbl.pack(side="right", padx=20)

        # ── Log panel ───────────────────────────────────────────
        log_frame = tk.Frame(self, bg=PANEL, bd=0, highlightthickness=1,
                              highlightbackground=BORDER)
        log_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        tk.Label(log_frame, text="Activity Log", font=("Georgia", 9),
                 fg=FG_DIM, bg=PANEL).pack(anchor="w", padx=12, pady=(8, 0))

        self._log_widget = scrolledtext.ScrolledText(
            log_frame, font=("Consolas", 9), bg="#0d0f18", fg=FG,
            insertbackground=FG, relief="flat", bd=0, state="disabled",
            wrap="word",
        )
        self._log_widget.pack(fill="both", expand=True, padx=8, pady=(4, 8))

    def _apply_log_tags(self):
        w = self._log_widget
        w.tag_config("ok",      foreground=SUCCESS)
        w.tag_config("warn",    foreground=WARN)
        w.tag_config("err",     foreground=ERR)
        w.tag_config("dim",     foreground=FG_DIM)
        w.tag_config("watch",   foreground=ACCENT2)
        w.tag_config("summary", foreground=ACCENT, font=("Consolas", 9, "bold"))
        w.tag_config("normal",  foreground=FG)

    # ── Callbacks ───────────────────────────────────────────────

    def _browse(self):
        d = filedialog.askdirectory(title="Select directory to organize")
        if d:
            self._dir_var.set(d)

    def _load_config(self):
        path = filedialog.askopenfilename(
            title="Select JSON config file",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            with open(path) as f:
                raw = json.load(f)
            self._mapping = {k: v for k, v in raw.items() if not k.startswith("_")}
            self._status("Config loaded: " + Path(path).name, ACCENT2)
        except Exception as e:
            messagebox.showerror("Config Error", str(e))

    def _clear_log(self):
        self._log_widget.configure(state="normal")
        self._log_widget.delete("1.0", "end")
        self._log_widget.configure(state="disabled")
        for lbl in self._stat_labels.values():
            lbl.config(text="0")

    def _status(self, text: str, color: str = FG_DIM):
        self._status_lbl.config(text=text, fg=color)

    def _update_stats(self, moved: int, skipped: int, errors: int):
        self._stat_labels["moved"].config(text=str(moved))
        self._stat_labels["skipped"].config(text=str(skipped))
        self._stat_labels["errors"].config(text=str(errors))

    # ── Run ─────────────────────────────────────────────────────

    def _make_logger(self, dry_run: bool) -> GUILogger:
        return GUILogger(self._log_widget, self._update_stats, dry_run=dry_run)

    def _run(self):
        directory = self._dir_var.get().strip()
        if not directory:
            messagebox.showwarning("No directory", "Please select a directory first.")
            return

        dry_run = self._dry_run_var.get()
        watch   = self._watch_var.get()

        self._clear_log()
        ext_index = build_ext_index(self._mapping)

        if watch:
            self._start_watch(directory, ext_index, dry_run)
        else:
            self._run_once(directory, ext_index, dry_run)

    def _run_once(self, directory: str, ext_index: dict, dry_run: bool):
        log = self._make_logger(dry_run)
        self._status("Organizing…", ACCENT)
        self._run_btn.config(state="disabled")

        def _work():
            path        = Path(directory).expanduser().resolve()
            script_name = Path(__file__).name
            try:
                for item_name in sorted(os.listdir(path)):
                    from organize import process_file
                    process_file(item_name, path, ext_index, script_name, log, dry_run)
                log.summary()
            finally:
                self.after(0, lambda: self._run_btn.config(state="normal"))
                self.after(0, lambda: self._status("Done ✓", SUCCESS))

        threading.Thread(target=_work, daemon=True).start()

    def _start_watch(self, directory: str, ext_index: dict, dry_run: bool):
        self._watching   = True
        self._watch_stop = threading.Event()
        self._run_btn.config(state="disabled")
        self._stop_btn.config(state="normal")
        self._status("Watching…", ACCENT2)

        log = self._make_logger(dry_run)

        def _work():
            from organize import process_file
            path        = Path(directory).expanduser().resolve()
            script_name = Path(__file__).name

            # Organize existing files first
            for item_name in sorted(os.listdir(path)):
                process_file(item_name, path, ext_index, script_name, log, dry_run=False)

            known = set(os.listdir(path))

            while not self._watch_stop.is_set():
                time.sleep(2)
                current   = set(os.listdir(path))
                new_files = current - known
                for item_name in sorted(new_files):
                    time.sleep(0.5)
                    log.watching(item_name)
                    process_file(item_name, path, ext_index, script_name, log, dry_run=False)
                known = set(os.listdir(path))

            log.summary()
            self.after(0, lambda: self._stop_btn.config(state="disabled"))
            self.after(0, lambda: self._run_btn.config(state="normal"))
            self.after(0, lambda: self._status("Watcher stopped", FG_DIM))

        threading.Thread(target=_work, daemon=True).start()

    def _stop_watch(self):
        self._watch_stop.set()
        self._watching = False


# ─────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = App()
    app.mainloop()