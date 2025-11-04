import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import threading
from datetime import datetime

API_URL = "https://open.er-api.com/v6/latest/USD"

# Some currency full names for display (partial)
CURRENCY_NAMES = {
    "USD": "United States Dollar",
    "EUR": "Euro",
    "GBP": "British Pound Sterling",
    "JPY": "Japanese Yen",
    "AUD": "Australian Dollar",
    "CAD": "Canadian Dollar",
    "CHF": "Swiss Franc",
    "CNY": "Chinese Yuan",
    "NZD": "New Zealand Dollar",
    "SEK": "Swedish Krona",
    "KRW": "South Korean Won",
    "SGD": "Singapore Dollar",
    "NOK": "Norwegian Krone",
    "MXN": "Mexican Peso",
    "INR": "Indian Rupee",
    "RUB": "Russian Ruble",
    "ZAR": "South African Rand",
    "TRY": "Turkish Lira",
    "BRL": "Brazilian Real",
    "TWD": "New Taiwan Dollar",
    "DKK": "Danish Krone",
    "PLN": "Polish Zloty",
    "THB": "Thai Baht",
    "IDR": "Indonesian Rupiah",
    # Add more if desired
}

class CurrencyConverterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Advanced Currency Converter")
        self.geometry("450x450")
        self.resizable(True, False)
        self.configure(bg="#764ba2")

        self.rates = {}
        self.last_update_unix = 0
        self.currencies = []

        # Variables
        self.from_currency_var = tk.StringVar()
        self.to_currency_var = tk.StringVar()
        self.amount_var = tk.StringVar()
        self.result_var = tk.StringVar()
        self.status_var = tk.StringVar()

        self.create_widgets()
        self.fetch_rates_async()

    def create_widgets(self):
        # Styling
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure("TLabel", background="#764ba2", foreground="white", font=("Poppins", 11))
        style.configure("TButton",
                        font=("Poppins", 11, "bold"),
                        foreground="white",
                        background="#6c63ff",
                        padding=6)
        style.configure("TEntry",
                        font=("Poppins", 11))
        style.configure("TCombobox",
                        font=("Poppins", 11),
                        foreground="#343")

        # Title
        title = ttk.Label(self, text="Currency Converter", font=("Poppins", 18, "bold"))
        title.pack(pady=(15, 10))

        frame = ttk.Frame(self)
        frame.pack(padx=20, pady=10, fill='x')

        # Amount Entry
        ttk.Label(frame, text="Amount:").grid(row=0, column=0, sticky='w', pady=5)
        amount_entry = ttk.Entry(frame, textvariable=self.amount_var)
        amount_entry.grid(row=0, column=1, sticky='ew', pady=5)
        amount_entry.focus()

        # From currency combobox
        ttk.Label(frame, text="From:").grid(row=1, column=0, sticky='w', pady=5)
        self.from_combo = ttk.Combobox(frame, textvariable=self.from_currency_var, state='readonly')
        self.from_combo.grid(row=1, column=1, sticky='ew', pady=5)

        # To currency combobox
        ttk.Label(frame, text="To:").grid(row=2, column=0, sticky='w', pady=5)
        self.to_combo = ttk.Combobox(frame, textvariable=self.to_currency_var, state='readonly')
        self.to_combo.grid(row=2, column=1, sticky='ew', pady=5)

        # Swap button
        self.swap_button = ttk.Button(frame, text="Swap ↔", command=self.swap_currencies)
        self.swap_button.grid(row=1, column=2, padx=10, sticky='ew', pady=5)

        # Convert button
        self.convert_button = ttk.Button(self, text="Convert", command=self.convert_currency)
        self.convert_button.pack(pady=12, ipadx=10)

        # Result label
        self.result_label = ttk.Label(self, textvariable=self.result_var, font=("Poppins", 14, "bold"), foreground="#ffd700")
        self.result_label.pack(pady=6)

        # Status label
        self.status_label = ttk.Label(self, textvariable=self.status_var, font=("Poppins", 9))
        self.status_label.pack(pady=3)

        # Configure grid weights
        frame.columnconfigure(1, weight=1)

    def fetch_rates_async(self):
        self.status_var.set("Loading exchange rates, please wait...")
        self.convert_button.config(state='disabled')
        self.swap_button.config(state='disabled')
        threading.Thread(target=self.fetch_rates).start()

    def fetch_rates(self):
        try:
            response = requests.get(API_URL, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get("result") == "error":
                self.status_var.set("API error: " + data.get("error-type", "Unknown error"))
                self.convert_button.config(state='normal')
                self.swap_button.config(state='normal')
                return
            self.rates = data.get("rates", {})
            self.last_update_unix = data.get("time_last_update_unix", 0)
            self.currencies = sorted(self.rates.keys())
            self.update_currency_widgets()
            self.status_var.set("Exchange rates updated at " + self.format_timestamp(self.last_update_unix))
            self.convert_button.config(state='normal')
            self.swap_button.config(state='normal')
        except requests.Timeout:
            self.status_var.set("Connection timed out. Please check your internet connection.")
        except requests.ConnectionError:
            self.status_var.set("Network connection error. Please check your internet connection.")
        except requests.RequestException as e:
            self.status_var.set(f"Failed to load exchange rates: {str(e)}")
        except json.JSONDecodeError:
            self.status_var.set("Invalid response from the server.")
        except Exception as e:
            self.status_var.set(f"Unexpected error: {str(e)}")
        finally:
            self.convert_button.config(state='normal')
            self.swap_button.config(state='normal')

    def update_currency_widgets(self):
        # Add currency names if available for display as "CODE - Name"
        display_values = [f"{code} - {CURRENCY_NAMES.get(code, 'Unknown')}" for code in self.currencies]

        self.from_combo['values'] = display_values
        self.to_combo['values'] = display_values

        # Set defaults
        try:
            default_from_index = self.currencies.index("USD")
        except ValueError:
            default_from_index = 0
        try:
            default_to_index = self.currencies.index("EUR")
        except ValueError:
            default_to_index = 1 if len(self.currencies) > 1 else 0

        self.from_combo.current(default_from_index)
        self.to_combo.current(default_to_index)

    def swap_currencies(self):
        from_idx = self.from_combo.current()
        to_idx = self.to_combo.current()
        self.from_combo.current(to_idx)
        self.to_combo.current(from_idx)
        self.result_var.set("")
        self.status_var.set("")

    def convert_currency(self):
        try:
            amount_text = self.amount_var.get().strip()
            if not amount_text:
                messagebox.showwarning("Input Error", "Please enter the amount to convert.")
                return
            amount = float(amount_text)
            if amount < 0:
                messagebox.showwarning("Input Error", "Please enter a non-negative amount.")
                return
        except ValueError:
            messagebox.showwarning("Input Error", "Invalid amount entered. Please enter a numeric value.")
            return

        from_idx = self.from_combo.current()
        to_idx = self.to_combo.current()
        if from_idx == -1 or to_idx == -1:
            messagebox.showwarning("Selection Error", "Please select both currencies.")
            return

        from_code = self.currencies[from_idx]
        to_code = self.currencies[to_idx]

        if from_code == to_code:
            self.result_var.set(f"{amount:.2f} {from_code} = {amount:.2f} {to_code}")
            return

        try:
            usd_amount = amount / self.rates[from_code]
            converted_amount = usd_amount * self.rates[to_code]
            self.result_var.set(f"{amount:.2f} {from_code} = {converted_amount:.2f} {to_code}")
            self.status_var.set("")
        except Exception as e:
            messagebox.showerror("Conversion Error", f"Error during conversion: {str(e)}")
            self.result_var.set("")
            self.status_var.set("")

    @staticmethod
    def format_timestamp(unix_timestamp):
        if unix_timestamp == 0:
            return "Unknown time"
        dt = datetime.utcfromtimestamp(unix_timestamp)
        return dt.strftime("%Y-%m-%d %H:%M UTC")

if __name__ == "__main__":
    app = CurrencyConverterApp()
    app.mainloop()
