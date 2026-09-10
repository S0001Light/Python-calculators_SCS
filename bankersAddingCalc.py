# Microsoft Co-Pilot built for us all

import tkinter as tk
from tkinter import ttk, filedialog
import csv
from decimal import Decimal, ROUND_HALF_UP

# -----------------------------
# Scrollable Frame Class
# -----------------------------
class ScrollableFrame(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)

        canvas = tk.Canvas(self, height=400)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

def money(x):
    # Currency symbols
    symbols = {
        "USD": "$",
    }

    symbol = symbols["USD"]

    # Format number to 2 decimals using Decimal
    value = x.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # Thousands separator toggle
    if separator_var.get():
        formatted = f"{value:,}"
    else:
        formatted = f"{value}"

    return f"{symbol}{formatted}"

# -----------------------------
# Addition Chain Generator
# -----------------------------

def generate_addition_chain():
    for widget in chain_frame.scrollable_frame.winfo_children():
        widget.destroy()

    start = Decimal(start_entry.get())
    increment = Decimal(increment_entry.get())

    steps = int(steps_entry.get())
    decimals = int(decimal_entry.get())

    fmt = f"{{:.{decimals}f}}"

    results.clear()

    ttk.Label(chain_frame.scrollable_frame, text="Addition Chain").grid(row=0, column=0, columnspan=3)

    ttk.Label(chain_frame.scrollable_frame, text="Step").grid(row=1, column=0)
    ttk.Label(chain_frame.scrollable_frame, text="Expected").grid(row=1, column=1)
    ttk.Label(chain_frame.scrollable_frame, text="Actual").grid(row=1, column=2)

    current = start

    for i in range(steps):
        expected = start + (increment * i)

        ttk.Label(chain_frame.scrollable_frame, text=str(i)).grid(row=i+2, column=0)
        ttk.Label(chain_frame.scrollable_frame, text=money(expected)).grid(row=i+2, column=1)

        actual_label = tk.Label(chain_frame.scrollable_frame, text=money(current), width=12)

        if current != expected:
            actual_label.config(bg="red", fg="white")
        else:
            actual_label.config(bg="white", fg="black")

        actual_label.grid(row=i+2, column=2)

        results.append((i, expected, current))
        current += increment


# -----------------------------
# CSV Export
# -----------------------------

def export_csv():
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV Files", "*.csv")]
    )
    if not file_path:
        return

    decimals = int(decimal_entry.get())
    fmt = f"{{:.{decimals}f}}"

    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Step", "Expected", "Actual"])

        for step, expected, actual in results:
            writer.writerow([step, money(expected), money(actual)])

# -----------------------------
# Main Window
# -----------------------------
app = tk.Tk()
app.title("Banker's Adding Calc")
app.config(bg="#202020")

results = []

input_frame = ttk.Frame(app)
input_frame.pack(pady=10)

ttk.Label(input_frame, text="Start Number:").grid(row=0, column=0)
start_entry = ttk.Entry(input_frame)
start_entry.grid(row=0, column=1)
start_entry.insert(0, "100")

ttk.Label(input_frame, text="Increment:").grid(row=1, column=0)
increment_entry = ttk.Entry(input_frame)
increment_entry.grid(row=1, column=1)
increment_entry.insert(0, "100")

ttk.Label(input_frame, text="Steps:").grid(row=2, column=0)
steps_entry = ttk.Entry(input_frame)
steps_entry.grid(row=2, column=1)
steps_entry.insert(0, "20")

ttk.Label(input_frame, text="Decimal Places:").grid(row=3, column=0)
decimal_entry = ttk.Entry(input_frame)
decimal_entry.grid(row=3, column=1)
decimal_entry.insert(0, "2")

separator_var = tk.BooleanVar(value=True)

ttk.Label(input_frame, text="Thousands Separator:").grid(row=6, column=0)
separator_check = ttk.Checkbutton(input_frame, variable=separator_var, text="Use Separator")
separator_check.grid(row=6, column=1)

ttk.Button(input_frame, text="Generate Chain", command=generate_addition_chain).grid(row=3, column=0, pady=10)
ttk.Button(input_frame, text="Export CSV", command=export_csv).grid(row=7, column=1, pady=10)

chain_frame = ScrollableFrame(app)
chain_frame.pack(padx=20, pady=10)

app.mainloop()
