from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Optional


class NumericKeypad(tk.Toplevel):
    """Touch-friendly keypad dialog used for quantity entry."""

    def __init__(self, parent: tk.Misc, initial_value: int = 1) -> None:
        super().__init__(parent)
        self.title("Enter quantity")
        self.resizable(False, False)
        self.configure(padx=12, pady=12)
        self.result: Optional[int] = None

        self._value_var = tk.StringVar(value=str(initial_value))

        label = ttk.Label(self, text="Quantity", font=("Segoe UI", 16, "bold"))
        label.pack(pady=(0, 12))

        entry = ttk.Entry(self, textvariable=self._value_var, font=("Segoe UI", 24), justify="center")
        entry.pack(fill="x", padx=4, pady=(0, 16))
        entry.focus_set()

        grid = ttk.Frame(self)
        grid.pack()
        buttons = [
            "1", "2", "3",
            "4", "5", "6",
            "7", "8", "9",
            "clear", "0", "del",
        ]
        for index, label_text in enumerate(buttons):
            btn = ttk.Button(
                grid,
                text=label_text.capitalize() if not label_text.isnumeric() else label_text,
                command=lambda value=label_text: self._handle_input(value),
                width=6,
            )
            row, col = divmod(index, 3)
            btn.grid(row=row, column=col, padx=4, pady=4, ipadx=4, ipady=8)

        action_frame = ttk.Frame(self)
        action_frame.pack(fill="x", pady=(12, 0))
        ttk.Button(action_frame, text="Cancel", command=self._cancel).pack(side="left", expand=True, fill="x", padx=(0, 6))
        ttk.Button(action_frame, text="OK", command=self._confirm).pack(side="right", expand=True, fill="x", padx=(6, 0))

        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._cancel)

    def _handle_input(self, value: str) -> None:
        if value == "clear":
            self._value_var.set("")
            return
        if value == "del":
            current = self._value_var.get()
            self._value_var.set(current[:-1])
            return
        self._value_var.set(self._value_var.get() + value)

    def _confirm(self) -> None:
        try:
            result = int(self._value_var.get())
        except ValueError:
            result = None
        if result is not None and result > 0:
            self.result = result
            self.destroy()
        else:
            self.bell()

    def _cancel(self) -> None:
        self.result = None
        self.destroy()


def prompt_quantity(parent: tk.Misc, initial_value: int = 1) -> Optional[int]:
    dialog = NumericKeypad(parent, initial_value=initial_value)
    parent.wait_window(dialog)
    return dialog.result


__all__ = ["NumericKeypad", "prompt_quantity"]
