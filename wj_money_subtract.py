from guizero import App, Box, Text, PushButton, TextBox, info
import tkinter as tk
from tkinter import ttk
import csv
from pathlib import Path


# ------------------------------------------------------------
# GRID SETTINGS
# ------------------------------------------------------------

ROWS = 150
COLS = 1
COL_NAMES = ["A"]

SAVE_FILE = Path(__file__).with_name("money_subtract_grid.csv")


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

        # Accounting-style negative number
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

    except ValueError:
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

    # Prevent -0.00
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

    # Start with first entered number
    result = numbers[0]

    # Subtract every following number
    for n in numbers[1:]:
        result -= n

    return result


# ------------------------------------------------------------
# UPDATE
# ------------------------------------------------------------

def update(*_):

    # There is only Column A
    result = subtract_col(0)

    # Update Column A subtraction result
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

    # Final result is the same as Column A
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
# ADD MONEY
# ------------------------------------------------------------

def add():

    value = num(amount.value)

    # Only Column A exists
    c = 0

    # Find first empty row
    for r in range(ROWS):

        if not values[r][c].get().strip():

            values[r][c].set(
                f"{value:.2f}"
            )

            update()

            entries[r][c].focus_set()

            # Scroll to the added entry
            entries[r][c].see if hasattr(entries[r][c], "see") else None

            return

    info(
        "Column full",
        "No empty row in Column A."
    )


# ------------------------------------------------------------
# CLEAR GRID
# ------------------------------------------------------------

def clear():

    for row in values:

        for variable in row:
            variable.set("")

    update()


# ------------------------------------------------------------
# SAVE
# ------------------------------------------------------------

def save():

    with SAVE_FILE.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.writer(f)

        writer.writerow(
            ["Row", "A"]
        )

        for r in range(ROWS):

            writer.writerow(
                [
                    r + 1,
                    values[r][0].get()
                ]
            )

    info(
        "Saved",
        f"Saved to:\n{SAVE_FILE}"
    )


# ------------------------------------------------------------
# LOAD
# ------------------------------------------------------------

def load():

    if not SAVE_FILE.exists():

        info(
            "Load",
            "No saved file yet."
        )

        return

    with SAVE_FILE.open(
        encoding="utf-8"
    ) as f:

        data = list(csv.reader(f))

    for r in range(ROWS):

        try:

            values[r][0].set(
                data[r + 1][1]
            )

        except IndexError:

            values[r][0].set("")

    update()


# ------------------------------------------------------------
# HEADER
# ------------------------------------------------------------

head = Box(
    app,
    width="fill",
    height=62,
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


# ------------------------------------------------------------
# CONTROLS
# ------------------------------------------------------------

controls = Box(
    app,
    width="fill",
    height=46,
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
    width=12
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
    text="Save",
    command=save,
    grid=[4, 0],
    width=7
)


PushButton(
    controls,
    text="Load",
    command=load,
    grid=[5, 0],
    width=7
)


# ------------------------------------------------------------
# SCROLLABLE GRID FRAME
# ------------------------------------------------------------

frame = tk.Frame(
    app.tk,
    bg="#ccc"
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

    # Row number
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
# START
# ------------------------------------------------------------

update()

app.display()
