from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional

from sinine_kapp.config import AppConfig
from sinine_kapp.models import Drink, User
from sinine_kapp.services.inventory_service import InventoryService
from sinine_kapp.services.lending_service import LendingService
from sinine_kapp.services.rfid_service import RFIDService
from sinine_kapp.services.transaction_service import TransactionService
from sinine_kapp.ui.components.keypad import prompt_quantity


class MainWindow(tk.Tk):
    def __init__(self, config: AppConfig, conn) -> None:
        super().__init__()
        self._config = config
        self._conn = conn
        self.title("Sinine Kapp - Drink Lending")
        self.geometry(f"{config.display_width}x{config.display_height}")
        self.minsize(800, 480)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.inventory_service = InventoryService(conn)
        self.lending_service = LendingService(conn)
        self.transaction_service = TransactionService(conn)
        self.rfid_service = RFIDService(conn, config, self._handle_user_scan)

        self.active_user: Optional[User] = None
        self.selected_drink: Optional[Drink] = None

        self.search_var = tk.StringVar()
        self.quantity_var = tk.IntVar(value=1)
        self.status_var = tk.StringVar(value="Waiting for user scan…")

        self._build_layout()
        self.refresh_inventory()
        self.refresh_transactions()
        self.rfid_service.start()

    def _build_layout(self) -> None:
        style = ttk.Style()
        style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"))
        style.configure("Value.TLabel", font=("Segoe UI", 16))

        container = ttk.Frame(self, padding=12)
        container.grid(row=0, column=0, sticky="nsew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        container.columnconfigure(0, weight=3)
        container.columnconfigure(1, weight=2)
        container.rowconfigure(0, weight=3)
        container.rowconfigure(1, weight=1)

        # Inventory list
        inventory_frame = ttk.Labelframe(container, text="Inventory")
        inventory_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 12), pady=(0, 12))
        inventory_frame.columnconfigure(0, weight=1)
        ttk.Entry(inventory_frame, textvariable=self.search_var).grid(
            row=0, column=0, sticky="ew", padx=8, pady=(8, 4)
        )
        self.search_var.trace_add("write", lambda *_: self.on_search())

        columns = ("name", "qty", "price", "volume")
        self.inventory_tree = ttk.Treeview(
            inventory_frame,
            columns=columns,
            show="headings",
            height=12,
        )
        self.inventory_tree.heading("name", text="Drink")
        self.inventory_tree.heading("qty", text="Qty")
        self.inventory_tree.heading("price", text="Price")
        self.inventory_tree.heading("volume", text="Volume")
        self.inventory_tree.column("name", width=220, anchor="w")
        self.inventory_tree.column("qty", width=70, anchor="center")
        self.inventory_tree.column("price", width=90, anchor="center")
        self.inventory_tree.column("volume", width=90, anchor="center")
        self.inventory_tree.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        inventory_frame.rowconfigure(1, weight=1)
        self.inventory_tree.bind("<<TreeviewSelect>>", self.on_drink_selected)

        # Action / user panel
        action_frame = ttk.Labelframe(container, text="Lend / Return")
        action_frame.grid(row=0, column=1, sticky="nsew", pady=(0, 12))
        action_frame.columnconfigure(0, weight=1)

        user_section = ttk.Frame(action_frame, padding=(8, 8))
        user_section.grid(row=0, column=0, sticky="ew")
        ttk.Label(user_section, text="Active User", style="Title.TLabel").pack(anchor="w")
        self.user_name_label = ttk.Label(user_section, text="No tag scanned", style="Value.TLabel")
        self.user_name_label.pack(anchor="w", pady=(4, 0))
        self.user_tag_label = ttk.Label(user_section, text="", font=("Segoe UI", 12))
        self.user_tag_label.pack(anchor="w")

        form = ttk.Frame(action_frame, padding=(8, 8))
        form.grid(row=1, column=0, sticky="nsew")
        form.columnconfigure(1, weight=1)

        ttk.Label(form, text="Selected drink:").grid(row=0, column=0, sticky="w")
        self.drink_value_label = ttk.Label(form, text="None")
        self.drink_value_label.grid(row=0, column=1, sticky="w")

        ttk.Label(form, text="Quantity:").grid(row=1, column=0, sticky="w", pady=(12, 0))
        qty_spin = ttk.Spinbox(
            form,
            from_=1,
            to=20,
            textvariable=self.quantity_var,
            width=5,
        )
        qty_spin.grid(row=1, column=1, sticky="w", pady=(12, 0))
        ttk.Button(form, text="Keypad", command=self.open_keypad).grid(
            row=1, column=2, padx=(8, 0), pady=(12, 0)
        )

        button_row = ttk.Frame(form)
        button_row.grid(row=2, column=0, columnspan=3, pady=(18, 0), sticky="ew")
        button_row.columnconfigure(0, weight=1)
        button_row.columnconfigure(1, weight=1)
        self.lend_button = ttk.Button(button_row, text="Lend", command=self.handle_lend)
        self.return_button = ttk.Button(button_row, text="Return", command=self.handle_return)
        self.lend_button.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.return_button.grid(row=0, column=1, sticky="ew", padx=(6, 0))

        self.sim_tag_var: Optional[tk.StringVar] = None
        if self._config.mock_rfid_reader:
            simulate_frame = ttk.Frame(form, padding=(0, 16))
            simulate_frame.grid(row=3, column=0, columnspan=3, sticky="ew")
            ttk.Label(simulate_frame, text="Simulate RFID tag:").pack(anchor="w")
            self.sim_tag_var = tk.StringVar()
            input_row = ttk.Frame(simulate_frame)
            input_row.pack(fill="x", pady=(4, 0))
            ttk.Entry(input_row, textvariable=self.sim_tag_var).pack(side="left", fill="x", expand=True)
            ttk.Button(input_row, text="Scan", command=self.simulate_scan).pack(side="left", padx=(8, 0))

        # Activity log
        log_frame = ttk.Labelframe(container, text="Recent Activity")
        log_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        columns = ("time", "user", "action")
        self.log_tree = ttk.Treeview(log_frame, columns=columns, show="headings", height=6)
        self.log_tree.heading("time", text="Time")
        self.log_tree.heading("user", text="User")
        self.log_tree.heading("action", text="Action")
        self.log_tree.column("time", width=140)
        self.log_tree.column("user", width=200)
        self.log_tree.column("action", width=200)
        self.log_tree.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        status = ttk.Label(self, textvariable=self.status_var, anchor="w", padding=8)
        status.grid(row=1, column=0, sticky="ew")

    def refresh_inventory(self, query: Optional[str] = None) -> None:
        if query:
            drinks = self.inventory_service.search_drinks(query)
        else:
            drinks = self.inventory_service.list_drinks()
        self._drink_cache = {str(drink.id): drink for drink in drinks}
        self.inventory_tree.delete(*self.inventory_tree.get_children())
        for drink in drinks:
            self.inventory_tree.insert(
                "",
                "end",
                iid=str(drink.id),
                values=(
                    drink.name,
                    drink.quantity_on_hand,
                    f"€{drink.unit_price:.2f}",
                    f"{drink.unit_volume_ml} ml",
                ),
            )

    def refresh_transactions(self) -> None:
        transactions = self.transaction_service.recent_transactions()
        self.log_tree.delete(*self.log_tree.get_children())
        for tx in transactions:
            label = f"{tx.action.capitalize()} {tx.quantity} × {tx.drink_name}"
            self.log_tree.insert("", "end", values=(tx.created_at.strftime("%H:%M"), tx.user_name, label))

    def on_search(self) -> None:
        text = self.search_var.get().strip()
        self.refresh_inventory(text if text else None)

    def on_drink_selected(self, _event=None) -> None:
        selected = self.inventory_tree.selection()
        if not selected:
            self.selected_drink = None
            self.drink_value_label.config(text="None")
            return
        drink_id = selected[0]
        drink = self._drink_cache.get(drink_id)
        if drink:
            self.selected_drink = drink
            self.drink_value_label.config(text=f"{drink.name} ({drink.quantity_on_hand} left)")

    def open_keypad(self) -> None:
        result = prompt_quantity(self, initial_value=self.quantity_var.get())
        if result:
            self.quantity_var.set(result)

    def _handle_user_scan(self, tag: str, user: Optional[User]) -> None:
        def apply_result() -> None:
            if user:
                self.active_user = user
                self.user_name_label.config(text=user.name)
                self.user_tag_label.config(text=f"Tag: {user.rfid_tag}")
                self.set_status(f"Ready for {user.name}")
            else:
                self.active_user = None
                self.user_name_label.config(text="Unknown tag")
                self.user_tag_label.config(text=tag)
                self.set_status("Unknown RFID tag", error=True)

        self.after(0, apply_result)

    def _process_action(self, action: str) -> None:
        if not self.active_user:
            messagebox.showinfo("Scan required", "Please scan a user tag first.")
            return
        if not self.selected_drink:
            messagebox.showinfo("Select drink", "Please choose a drink from the list")
            return
        quantity = self.quantity_var.get()
        try:
            if action == "lend":
                self.lending_service.lend(self.active_user.id, self.selected_drink.id, quantity)
                self.set_status(f"Lent {quantity} × {self.selected_drink.name} to {self.active_user.name}")
            else:
                self.lending_service.return_drink(self.active_user.id, self.selected_drink.id, quantity)
                self.set_status(f"Returned {quantity} × {self.selected_drink.name}")
            self.refresh_inventory(self.search_var.get().strip() or None)
            self.refresh_transactions()
        except ValueError as exc:
            messagebox.showerror("Unable to process", str(exc))
            self.set_status(str(exc), error=True)

    def handle_lend(self) -> None:
        self._process_action("lend")

    def handle_return(self) -> None:
        self._process_action("return")

    def simulate_scan(self) -> None:
        if not self.sim_tag_var:
            return
        tag = self.sim_tag_var.get().strip()
        if tag:
            self.rfid_service.simulate_scan(tag)

    def set_status(self, text: str, *, error: bool = False) -> None:
        self.status_var.set(text)
        if error:
            self.bell()

    def _on_close(self) -> None:
        self.rfid_service.stop()
        self.destroy()


__all__ = ["MainWindow"]
