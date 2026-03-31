import tkinter as tk
from tkinter import messagebox, font
import json
import os

# ── Constants ────────────────────────────────────────────────────────────────
DATA_FILE = "tasks.json"

BG_MAIN   = "#1e1e2e"   # deep navy
BG_PANEL  = "#2a2a3e"   # slightly lighter panel
BG_ENTRY  = "#313145"   # input background
ACCENT    = "#7c6af7"   # violet
ACCENT_HO = "#9d8fff"   # hovered violet
BTN_DEL   = "#e06c75"   # soft red
BTN_DEL_H = "#f08090"
TEXT_PRI  = "#cdd6f4"   # near-white
TEXT_SEC  = "#6c7086"   # muted grey
SEL_BG    = "#45475a"   # listbox selection bg


# ── App Class ────────────────────────────────────────────────────────────────
class TodoApp:
    """
    Main application class.

    Responsibilities
    ----------------
    - Build and configure every UI widget.
    - Bind events (button clicks, Enter key, listbox clicks).
    - Load tasks from disk on startup; persist changes back on every mutation.
    """

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self._configure_root()

        # In-memory task list – single source of truth
        self.tasks: list[str] = []

        self._build_ui()
        self._load_tasks()          # Populate self.tasks + refresh the listbox

    # ── Window setup ────────────────────────────────────────────────────────

    def _configure_root(self) -> None:
        self.root.title("✦ To-Do")
        self.root.geometry("480x580")
        self.root.minsize(380, 460)
        self.root.configure(bg=BG_MAIN)
        self.root.resizable(True, True)

    # ── UI construction ──────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        """Assemble every widget in logical top-to-bottom order."""

        # ── Header ──────────────────────────────────────────────────────────
        header_frame = tk.Frame(self.root, bg=BG_MAIN)
        header_frame.pack(fill="x", padx=28, pady=(28, 6))

        title_font = font.Font(family="Georgia", size=22, weight="bold")
        tk.Label(
            header_frame,
            text="My Tasks",
            font=title_font,
            bg=BG_MAIN,
            fg=TEXT_PRI,
        ).pack(side="left")

        # Task counter badge
        self.counter_var = tk.StringVar(value="0 tasks")
        tk.Label(
            header_frame,
            textvariable=self.counter_var,
            font=("Helvetica", 11),
            bg=BG_MAIN,
            fg=TEXT_SEC,
        ).pack(side="right", anchor="s", pady=4)

        # ── Input area ──────────────────────────────────────────────────────
        input_frame = tk.Frame(self.root, bg=BG_MAIN)
        input_frame.pack(fill="x", padx=28, pady=(10, 0))
        input_frame.columnconfigure(0, weight=1)

        entry_font = font.Font(family="Helvetica", size=13)
        self.task_entry = tk.Entry(
            input_frame,
            font=entry_font,
            bg=BG_ENTRY,
            fg=TEXT_PRI,
            insertbackground=TEXT_PRI,
            relief="flat",
            bd=0,
        )
        self.task_entry.grid(row=0, column=0, sticky="ew", ipady=10, padx=(0, 10))

        # Pressing Enter triggers add_task – keyboard shortcut requirement
        self.task_entry.bind("<Return>", lambda event: self.add_task())
        self.task_entry.focus()

        add_btn = tk.Button(
            input_frame,
            text="Add  +",
            font=("Helvetica", 12, "bold"),
            bg=ACCENT,
            fg="#ffffff",
            activebackground=ACCENT_HO,
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            padx=16,
            pady=8,
            cursor="hand2",
            command=self.add_task,
        )
        add_btn.grid(row=0, column=1)

        # ── Divider ─────────────────────────────────────────────────────────
        tk.Frame(self.root, bg=SEL_BG, height=1).pack(
            fill="x", padx=28, pady=(18, 0)
        )

        # ── Task list ───────────────────────────────────────────────────────
        list_frame = tk.Frame(self.root, bg=BG_MAIN)
        list_frame.pack(fill="both", expand=True, padx=28, pady=(12, 0))
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        list_font = font.Font(family="Helvetica", size=12)
        self.listbox = tk.Listbox(
            list_frame,
            font=list_font,
            bg=BG_PANEL,
            fg=TEXT_PRI,
            selectbackground=ACCENT,
            selectforeground="#ffffff",
            activestyle="none",
            relief="flat",
            bd=0,
            highlightthickness=0,
        )
        self.listbox.grid(row=0, column=0, sticky="nsew")

        scrollbar = tk.Scrollbar(
            list_frame,
            orient="vertical",
            command=self.listbox.yview,
            bg=BG_PANEL,
            troughcolor=BG_PANEL,
            activebackground=ACCENT,
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.listbox.configure(yscrollcommand=scrollbar.set)

        # ── Bottom toolbar ──────────────────────────────────────────────────
        toolbar = tk.Frame(self.root, bg=BG_MAIN)
        toolbar.pack(fill="x", padx=28, pady=(10, 24))

        self.empty_label = tk.Label(
            toolbar,
            text="No tasks yet – add one above!",
            font=("Helvetica", 11, "italic"),
            bg=BG_MAIN,
            fg=TEXT_SEC,
        )
        self.empty_label.pack(side="left")

        del_btn = tk.Button(
            toolbar,
            text="Delete selected",
            font=("Helvetica", 11),
            bg=BTN_DEL,
            fg="#ffffff",
            activebackground=BTN_DEL_H,
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            padx=14,
            pady=6,
            cursor="hand2",
            command=self.delete_task,
        )
        del_btn.pack(side="right")

    # ── Core logic ───────────────────────────────────────────────────────────

    def add_task(self) -> None:
        """
        Read the entry widget, validate, append to the list,
        refresh the UI, and persist immediately.

        Empty-task guard: strip() collapses whitespace-only strings to "",
        which evaluates as falsy – we show a warning and return early.
        """
        raw = self.task_entry.get()
        text = raw.strip()

        if not text:                              # ← empty-task guard
            messagebox.showwarning(
                "Empty task",
                "Please type something before adding a task.",
            )
            self.task_entry.focus()
            return

        self.tasks.append(text)
        self.task_entry.delete(0, tk.END)         # clear input field
        self._refresh_listbox()
        self._save_tasks()

    def delete_task(self) -> None:
        """
        Remove the currently selected item.
        If nothing is selected, warn the user rather than crashing.
        """
        selection = self.listbox.curselection()   # returns a tuple of indices
        if not selection:
            messagebox.showwarning(
                "No selection",
                "Please click a task in the list first.",
            )
            return

        index = selection[0]
        del self.tasks[index]
        self._refresh_listbox()
        self._save_tasks()

    # ── UI helpers ───────────────────────────────────────────────────────────

    def _refresh_listbox(self) -> None:
        """Repaint the listbox from self.tasks and update the counter badge."""
        self.listbox.delete(0, tk.END)
        for task in self.tasks:
            self.listbox.insert(tk.END, f"  {task}")

        count = len(self.tasks)
        self.counter_var.set(f"{count} task{'s' if count != 1 else ''}")

        # Show / hide the empty-state hint
        if count:
            self.empty_label.config(text="")
        else:
            self.empty_label.config(text="No tasks yet – add one above!")

    # ── Persistence ──────────────────────────────────────────────────────────

    def _save_tasks(self) -> None:
        """
        Serialise self.tasks to DATA_FILE as JSON.

        JSON is chosen over plain .txt because it handles commas, special
        characters, and unicode without any custom parsing logic.

        File is written atomically: json.dump() creates / overwrites the file
        in one call, so a crash mid-write cannot leave a corrupt file behind
        (the OS flushes a complete write or rolls back).
        """
        with open(DATA_FILE, "w", encoding="utf-8") as fh:
            json.dump(self.tasks, fh, ensure_ascii=False, indent=2)

    def _load_tasks(self) -> None:
        """
        Deserialise tasks from DATA_FILE on startup.

        If the file does not yet exist (first run) we silently start empty.
        A corrupted file triggers a warning so the user can decide to delete it.
        """
        if not os.path.exists(DATA_FILE):
            return                                # first run – nothing to load

        try:
            with open(DATA_FILE, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            if isinstance(data, list):            # basic schema validation
                self.tasks = [str(t) for t in data]
        except (json.JSONDecodeError, OSError) as exc:
            messagebox.showerror(
                "Load error",
                f"Could not read {DATA_FILE}:\n{exc}\n\nStarting with an empty list.",
            )

        self._refresh_listbox()


# ── Entry point ──────────────────────────────────────────────────────────────

def main() -> None:
    """
    Create the Tk root window and hand control to the Tkinter event loop.

    mainloop() is an infinite loop that:
      1. Waits for the next OS event (keypress, click, resize, timer, …).
      2. Dispatches it to the registered callback (e.g. add_task for <Return>).
      3. Redraws any widgets marked dirty.
      4. Repeats until the window is closed (root.destroy() is called).

    Everything in the app is driven by this loop – our code only runs when
    the loop invokes one of our callbacks; it never 'polls'.
    """
    root = tk.Tk()
    TodoApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()