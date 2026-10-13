from guizero import App, Box, Text, PushButton, TextBox, info
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
from pathlib import Path


# ------------------------------------------------------------
# GRID SETTINGS
# ------------------------------------------------------------

ROWS = 150
COLS = 1
COL_NAMES = ["A"]

DEFAULT_FOLDER = Path(__file__).resolve().parent
DEFAULT_FILE_NAME = "money_subtract_grid.csv"

# Tracks the file most recently loaded or saved.
current_file = None


# ------------------------------------------------------------
# APP
# ------------------------------------------------------------

app = App(
    title="Money Subtract Grid",
    width=520,
    height=760,
    bg="#eef3f8"
)

values = [[None] * COLS for _ in range(ROWS)]
entries = [[None] * COLS for _ in range(ROWS)]

col_results = []


# ------------------------------------------------------------
# NUMBER FUNCTIONS
# ------------------------------------------------------------

def num(x):
    """
    Convert entered text to a floating-point number.

    Handles:
        123.45
        $123.45
        1,234.56
        ($123.45)
        -123.45
    """

    try:
        text = str(x).strip()

        if not text:
            return 0.0

        negative = False

        # Accounting-style negative number.
        if text.startswith("(") and text.endswith(")"):
            negative = True
            text = text[1:-1]

        text = text.replace("$", "")
        text = text.replace(",", "")
        text = text.strip()

        value = float(text)

        if negative:
            value = -abs(value)

        return value

    except (ValueError, TypeError):
        return 0.0


def money(x):
    """
    Format money.

    Positive:
        $125.50

    Negative:
        ($125.50)

    Zero:
        $0.00
    """

    # Prevent -0.00.
    if abs(x) < 0.005:
        x = 0.0

    if x < 0:
        return f"(${abs(x):,.2f})"

    return f"${x:,.2f}"


# ------------------------------------------------------------
# COLUMN CALCULATION
# ------------------------------------------------------------

def subtract_col(c):
    numbers = []

    for r in range(ROWS):
        text = values[r][c].get().strip()

        if text:
            numbers.append(num(text))

    if not numbers:
        return 0.0

    # Start with the first entered number.
    result = numbers[0]

    # Subtract every following number.
    for n in numbers[1:]:
        result -= n

    return result


# ------------------------------------------------------------
# UPDATE
# ------------------------------------------------------------

def update(*_):
    # There is only Column A.
    result = subtract_col(0)

    # Update Column A subtraction result.
    col_results[0].config(
        text=money(result)
    )

    if result < 0:
        col_results[0].config(
            fg="#8b0000",
            bg="#ffe1e1"
        )
    else:
        col_results[0].config(
            fg="#164d24",
            bg="#e6f4e8"
        )

    # Final result is the same as Column A.
    final_result.config(
        text=money(result)
    )

    if result < 0:
        final_result.config(
            fg="#8b0000",
            bg="#ffe1e1"
        )
    else:
        final_result.config(
            fg="#164d24",
            bg="#e6f4e8"
        )


# ------------------------------------------------------------
# WINDOW TITLE
# ------------------------------------------------------------

def update_window_title():
    if current_file is None:
        app.title = "Money Subtract Grid"
        current_file_label.value = "No file selected"
    else:
        app.title = f"Money Subtract Grid - {current_file.name}"
        current_file_label.value = current_file.name


# ------------------------------------------------------------
# ADD MONEY
# ------------------------------------------------------------

def add():
    text = amount.value.strip()

    if not text:
        info(
            "Enter Amount",
            "Enter an amount before clicking Add."
        )
        return

    value = num(text)

    # Only Column A exists.
    c = 0

    # Find the first empty row.
    for r in range(ROWS):
        if not values[r][c].get().strip():
            values[r][c].set(f"{value:.2f}")

            update()

            entries[r][c].focus_set()
            entries[r][c].selection_range(0, tk.END)

            # Scroll the canvas near the newly added row.
            position = r / max(1, ROWS - 1)
            canvas.yview_moveto(position)

            return

    info(
        "Column Full",
        "No empty row is available in Column A."
    )


# ------------------------------------------------------------
# CLEAR GRID
# ------------------------------------------------------------

def clear():
    answer = messagebox.askyesno(
        "Clear Grid",
        "Clear all 150 rows?"
    )

    if not answer:
        return

    for row in values:
        for variable in row:
            variable.set("")

    update()

    canvas.yview_moveto(0)
    entries[0][0].focus_set()


# ------------------------------------------------------------
# WRITE CSV FILE
# ------------------------------------------------------------

def write_csv(file_path):
    file_path = Path(file_path)

    try:
        with file_path.open(
            "w",
            newline="",
            encoding="utf-8"
        ) as f:
            writer = csv.writer(f)

            writer.writerow(["Row", "A"])

            for r in range(ROWS):
                writer.writerow(
                    [
                        r + 1,
                        values[r][0].get()
                    ]
                )

        return True

    except OSError as error:
        messagebox.showerror(
            "Save Error",
            f"The file could not be saved.\n\n{error}"
        )
        return False


# ------------------------------------------------------------
# SAVE AS
# ------------------------------------------------------------

def save_as():
    global current_file

    if current_file is not None:
        initial_directory = current_file.parent
        initial_file = current_file.name
    else:
        initial_directory = DEFAULT_FOLDER
        initial_file = DEFAULT_FILE_NAME

    selected_file = filedialog.asksaveasfilename(
        parent=app.tk,
        title="Save Money Subtract Grid As",
        initialdir=str(initial_directory),
        initialfile=initial_file,
        defaultextension=".csv",
        filetypes=[
            ("CSV files", "*.csv"),
            ("All files", "*.*")
        ]
    )

    if not selected_file:
        return

    selected_path = Path(selected_file)

    if write_csv(selected_path):
        current_file = selected_path
        update_window_title()

        info(
            "Saved",
            f"Saved to:\n{current_file}"
        )


# ------------------------------------------------------------
# FIND NEXT NUMBERED FILE
# ------------------------------------------------------------

def get_next_numbered_file():
    """
    Finds an unused numbered filename.

    Examples:
        money_subtract_grid_1.csv
        money_subtract_grid_2.csv
        money_subtract_grid_3.csv
    """

    if current_file is not None:
        folder = current_file.parent
        original_stem = current_file.stem
    else:
        folder = DEFAULT_FOLDER
        original_stem = Path(DEFAULT_FILE_NAME).stem

    # Remove an existing ending such as _1, _2, _25.
    parts = original_stem.rsplit("_", 1)

    if len(parts) == 2 and parts[1].isdigit():
        base_stem = parts[0]
    else:
        base_stem = original_stem

    number = 1

    while True:
        candidate = folder / f"{base_stem}_{number}.csv"

        if not candidate.exists():
            return candidate

        number += 1


# ------------------------------------------------------------
# SAVE NEXT NUMBERED FILE
# ------------------------------------------------------------

def save_next():
    global current_file

    selected_path = get_next_numbered_file()

    if write_csv(selected_path):
        current_file = selected_path
        update_window_title()

        info(
            "Saved",
            f"Saved numbered copy:\n{current_file}"
        )


# ------------------------------------------------------------
# LOAD ANY CSV FILE
# ------------------------------------------------------------

def load_file():
    global current_file

    if current_file is not None:
        initial_directory = current_file.parent
    else:
        initial_directory = DEFAULT_FOLDER

    selected_file = filedialog.askopenfilename(
        parent=app.tk,
        title="Open Money Grid File",
        initialdir=str(initial_directory),
        filetypes=[
            ("CSV files", "*.csv"),
            ("Text files", "*.txt"),
            ("All files", "*.*")
        ]
    )

    if not selected_file:
        return

    selected_path = Path(selected_file)

    try:
        with selected_path.open(
            "r",
            newline="",
            encoding="utf-8-sig"
        ) as f:
            data = list(csv.reader(f))

    except (OSError, UnicodeError, csv.Error) as error:
        messagebox.showerror(
            "Load Error",
            f"The file could not be loaded.\n\n{error}"
        )
        return

    # Clear the existing grid before loading.
    for r in range(ROWS):
        values[r][0].set("")

    if not data:
        current_file = selected_path
        update_window_title()
        update()

        info(
            "Loaded",
            "The selected file was empty."
        )
        return

    start_row = 0

    # Detect the normal heading written by this program.
    first_row = data[0]

    if first_row:
        first_cell = first_row[0].strip().lower()

        if first_cell in ("row", "#"):
            start_row = 1

    grid_row = 0

    for csv_row in data[start_row:]:
        if grid_row >= ROWS:
            break

        if not csv_row:
            continue

        loaded_value = ""

        # Normal program format:
        # Row,A
        # 1,100.00
        if len(csv_row) >= 2:
            loaded_value = csv_row[1].strip()

        # Single-column CSV format:
        # 100.00
        # 25.00
        elif len(csv_row) == 1:
            loaded_value = csv_row[0].strip()

        values[grid_row][0].set(loaded_value)
        grid_row += 1

    current_file = selected_path

    update()
    update_window_title()
    canvas.yview_moveto(0)

    info(
        "Loaded",
        f"Loaded {grid_row} rows from:\n{current_file}"
    )


# ------------------------------------------------------------
# HEADER
# ------------------------------------------------------------

head = Box(
    app,
    width="fill",
    height=78,
    align="top"
)

head.bg = "#612020"

Text(
    head,
    text="Money Subtract Grid",
    size=19,
    bold=True,
    color="white"
)

Text(
    head,
    text="Column A - 150 Rows",
    size=10,
    color="#ffe1e1"
)

current_file_label = Text(
    head,
    text="No file selected",
    size=9,
    color="#ffd6d6"
)


# ------------------------------------------------------------
# CONTROLS
# ------------------------------------------------------------

controls = Box(
    app,
    width="fill",
    height=82,
    layout="grid",
    align="top"
)

controls.bg = "white"

Text(
    controls,
    text="Amount $",
    grid=[0, 0],
    bold=True
)

amount = TextBox(
    controls,
    text="100.00",
    grid=[1, 0],
    width=13
)

PushButton(
    controls,
    text="Add",
    command=add,
    grid=[2, 0],
    width=7
)

PushButton(
    controls,
    text="Clear",
    command=clear,
    grid=[3, 0],
    width=7
)

PushButton(
    controls,
    text="Load File",
    command=load_file,
    grid=[0, 1],
    width=10
)

PushButton(
    controls,
    text="Save As",
    command=save_as,
    grid=[1, 1],
    width=10
)

PushButton(
    controls,
    text="Save Next",
    command=save_next,
    grid=[2, 1],
    width=10
)

Text(
    controls,
    text="Save Next creates _1, _2, _3...",
    grid=[3, 1],
    size=8,
    color="#612020"
)


# ------------------------------------------------------------
# SCROLLABLE GRID FRAME
# ------------------------------------------------------------

frame = tk.Frame(
    app.tk,
    bg="#cccccc"
)

frame.pack(
    fill="both",
    expand=True,
    padx=6,
    pady=6
)

frame.rowconfigure(
    0,
    weight=1
)

frame.columnconfigure(
    0,
    weight=1
)


# ------------------------------------------------------------
# CANVAS
# ------------------------------------------------------------

canvas = tk.Canvas(
    frame,
    bg="white",
    highlightthickness=0
)

vs = ttk.Scrollbar(
    frame,
    orient="vertical",
    command=canvas.yview
)

hs = ttk.Scrollbar(
    frame,
    orient="horizontal",
    command=canvas.xview
)

canvas.configure(
    yscrollcommand=vs.set,
    xscrollcommand=hs.set
)

canvas.grid(
    row=0,
    column=0,
    sticky="nsew"
)

vs.grid(
    row=0,
    column=1,
    sticky="ns"
)

hs.grid(
    row=1,
    column=0,
    sticky="ew"
)


# ------------------------------------------------------------
# SPREADSHEET AREA
# ------------------------------------------------------------

sheet = tk.Frame(
    canvas,
    bg="white"
)

canvas_window = canvas.create_window(
    (0, 0),
    window=sheet,
    anchor="nw"
)


# ------------------------------------------------------------
# UPDATE SCROLL REGION
# ------------------------------------------------------------

def update_scroll_region(event=None):
    canvas.configure(
        scrollregion=canvas.bbox("all")
    )


sheet.bind(
    "<Configure>",
    update_scroll_region
)


# ------------------------------------------------------------
# MOUSE WHEEL
# ------------------------------------------------------------

def mousewheel(event):
    if event.delta:
        canvas.yview_scroll(
            int(-event.delta / 120),
            "units"
        )


canvas.bind_all(
    "<MouseWheel>",
    mousewheel
)


# ------------------------------------------------------------
# GRID STYLES
# ------------------------------------------------------------

font = (
    "Segoe UI",
    9
)

bold = (
    "Segoe UI",
    9,
    "bold"
)

hdr = {
    "bg": "#612020",
    "fg": "white",
    "font": bold,
    "bd": 1,
    "relief": "solid",
    "padx": 4,
    "pady": 4
}


# ------------------------------------------------------------
# COLUMN HEADER
# ------------------------------------------------------------

tk.Label(
    sheet,
    text="#",
    width=5,
    **hdr
).grid(
    row=0,
    column=0,
    sticky="nsew"
)

tk.Label(
    sheet,
    text="A",
    width=20,
    **hdr
).grid(
    row=0,
    column=1,
    sticky="nsew"
)


# ------------------------------------------------------------
# 150 ROW DATA GRID
# ------------------------------------------------------------

for r in range(ROWS):
    # Row number.
    tk.Label(
        sheet,
        text=r + 1,
        width=5,
        bg="#eeeeee",
        font=bold,
        bd=1,
        relief="solid"
    ).grid(
        row=r + 1,
        column=0,
        sticky="nsew"
    )

    variable = tk.StringVar()
    values[r][0] = variable

    entry = tk.Entry(
        sheet,
        textvariable=variable,
        width=20,
        justify="right",
        font=font,
        bd=1,
        relief="solid"
    )

    entry.grid(
        row=r + 1,
        column=1,
        sticky="nsew"
    )

    entry.bind(
        "<KeyRelease>",
        update
    )

    entry.bind(
        "<FocusOut>",
        update
    )

    entries[r][0] = entry


# ------------------------------------------------------------
# SUBTRACTION ROW
# ------------------------------------------------------------

tr = ROWS + 1

tk.Label(
    sheet,
    text="SUB",
    width=5,
    **hdr
).grid(
    row=tr,
    column=0,
    sticky="nsew"
)

result_label = tk.Label(
    sheet,
    text="$0.00",
    width=20,
    anchor="e",
    bg="#e6f4e8",
    fg="#164d24",
    font=bold,
    bd=1,
    relief="solid"
)

result_label.grid(
    row=tr,
    column=1,
    sticky="nsew"
)

col_results.append(
    result_label
)


# ------------------------------------------------------------
# FINAL RESULT
# ------------------------------------------------------------

tk.Label(
    sheet,
    text="COLUMN A RESULT",
    bg="#612020",
    fg="white",
    font=bold,
    bd=1,
    relief="solid",
    padx=5,
    pady=5
).grid(
    row=tr + 1,
    column=0,
    sticky="nsew"
)

final_result = tk.Label(
    sheet,
    text="$0.00",
    anchor="e",
    bg="#e6f4e8",
    fg="#164d24",
    font=("Segoe UI", 10, "bold"),
    bd=1,
    relief="solid",
    padx=5,
    pady=5
)

final_result.grid(
    row=tr + 1,
    column=1,
    sticky="nsew"
)


# ------------------------------------------------------------
# KEYBOARD SHORTCUTS
# ------------------------------------------------------------

app.tk.bind(
    "<Control-o>",
    lambda event: load_file()
)

app.tk.bind(
    "<Control-Shift-S>",
    lambda event: save_as()
)

app.tk.bind(
    "<Control-s>",
    lambda event: save_next()
)

amount.tk.bind(
    "<Return>",
    lambda event: add()
)


# ------------------------------------------------------------
# START
# ------------------------------------------------------------

update()
update_window_title()

app.display()
