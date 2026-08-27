import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import matplotlib.pyplot as plt


# =========================================================
# GLOBAL VARIABLES
# =========================================================

data = None
cleaned_data = None
displayed_data = None

file_path = ""


# =========================================================
# CHOOSE CSV FILE
# =========================================================

def choose_file():

    global data
    global cleaned_data
    global displayed_data
    global file_path

    file_path = filedialog.askopenfilename(
        title="Choose CSV File",
        filetypes=[
            ("CSV Files", "*.csv"),
            ("All Files", "*.*")
        ]
    )

    if not file_path:
        return

    try:

        data = pd.read_csv(file_path)

        cleaned_data = None
        displayed_data = data.copy()

        file_label.config(
            text="File: " + file_path
        )

        display_data(data)

        update_column_list(data)

        update_dashboard(data)

        status_label.config(
            text="CSV file loaded successfully."
        )

        output_text.delete(
            "1.0",
            tk.END
        )

        output_text.insert(
            tk.END,
            f"File loaded successfully!\n\n"
            f"Rows: {len(data)}\n"
            f"Columns: {len(data.columns)}\n"
        )

    except Exception as e:

        messagebox.showerror(
            "Error",
            f"Could not read CSV file.\n\n{e}"
        )


# =========================================================
# DISPLAY DATA
# =========================================================

def display_data(df):

    global displayed_data

    displayed_data = df.copy()

    # Clear table
    for item in tree.get_children():
        tree.delete(item)

    # Set columns
    tree["columns"] = list(df.columns)

    tree["show"] = "headings"

    for column in df.columns:

        tree.heading(
            column,
            text=column
        )

        tree.column(
            column,
            width=120,
            anchor="center"
        )

    # Add rows
    for _, row in df.iterrows():

        values = []

        for value in row:

            if pd.isna(value):
                values.append("")
            else:
                values.append(value)

        tree.insert(
            "",
            "end",
            values=values
        )


# =========================================================
# UPDATE COLUMN LIST
# =========================================================

def update_column_list(df):

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns.tolist()

    column_combo["values"] = numeric_columns

    if numeric_columns:

        column_combo.current(0)

    else:

        column_combo.set("")


# =========================================================
# DASHBOARD
# =========================================================

def update_dashboard(df):

    rows_value.config(
        text=str(len(df))
    )

    columns_value.config(
        text=str(len(df.columns))
    )

    missing_value.config(
        text=str(df.isnull().sum().sum())
    )

    duplicate_value.config(
        text=str(df.duplicated().sum())
    )


# =========================================================
# SHOW INFORMATION
# =========================================================

def show_info():

    global data

    if data is None:

        messagebox.showwarning(
            "Warning",
            "Please choose a CSV file first."
        )

        return

    result = ""

    result += "========== DATA INFORMATION ==========\n\n"

    result += f"Rows: {data.shape[0]}\n"
    result += f"Columns: {data.shape[1]}\n\n"

    result += "Column Names:\n"

    for column in data.columns:

        result += f"  - {column}\n"

    result += "\nData Types:\n"

    for column in data.columns:

        result += (
            f"  {column}: "
            f"{data[column].dtype}\n"
        )

    result += "\nMissing Values:\n"

    for column, value in data.isnull().sum().items():

        result += (
            f"  {column}: {value}\n"
        )

    result += (
        f"\nDuplicate Rows: "
        f"{data.duplicated().sum()}\n"
    )

    output_text.delete(
        "1.0",
        tk.END
    )

    output_text.insert(
        tk.END,
        result
    )


# =========================================================
# CLEAN DATA
# =========================================================

def clean_data():

    global data
    global cleaned_data

    if data is None:

        messagebox.showwarning(
            "Warning",
            "Please choose a CSV file first."
        )

        return

    try:

        cleaned_data = data.copy()

        original_rows = len(cleaned_data)

        original_missing = (
            cleaned_data.isnull().sum().sum()
        )

        # -------------------------------------------------
        # CLEAN COLUMN NAMES
        # -------------------------------------------------

        cleaned_data.columns = (
            cleaned_data.columns
            .str.strip()
            .str.lower()
            .str.replace(" ", "_", regex=False)
        )

        # -------------------------------------------------
        # REMOVE DUPLICATES
        # -------------------------------------------------

        duplicate_count = (
            cleaned_data.duplicated().sum()
        )

        cleaned_data = (
            cleaned_data
            .drop_duplicates()
            .reset_index(drop=True)
        )

        # -------------------------------------------------
        # CLEAN TEXT
        # -------------------------------------------------

        text_columns = cleaned_data.select_dtypes(
            include="object"
        ).columns

        for column in text_columns:

            cleaned_data[column] = (
                cleaned_data[column]
                .astype("string")
                .str.strip()
            )

        # -------------------------------------------------
        # CONVERT NUMERIC-LOOKING COLUMNS
        # -------------------------------------------------

        for column in cleaned_data.columns:

            if (
                cleaned_data[column].dtype
                == "string"
            ):

                converted = pd.to_numeric(
                    cleaned_data[column],
                    errors="coerce"
                )

                valid_values = converted.notna().sum()

                total_values = len(
                    cleaned_data[column]
                )

                if (
                    total_values > 0
                    and
                    valid_values / total_values >= 0.7
                ):

                    cleaned_data[column] = converted

        # -------------------------------------------------
        # HANDLE MISSING VALUES
        # -------------------------------------------------

        for column in cleaned_data.columns:

            if pd.api.types.is_numeric_dtype(
                cleaned_data[column]
            ):

                if cleaned_data[column].notna().any():

                    median = cleaned_data[
                        column
                    ].median()

                    cleaned_data[column] = (
                        cleaned_data[column]
                        .fillna(median)
                    )

            else:

                cleaned_data[column] = (
                    cleaned_data[column]
                    .fillna("Unknown")
                )

        # -------------------------------------------------
        # SCORE FEATURES
        # -------------------------------------------------

        if "score" in cleaned_data.columns:

            # Keep scores within 0-100
            cleaned_data = cleaned_data[
                (cleaned_data["score"] >= 0)
                &
                (cleaned_data["score"] <= 100)
            ].copy()

            # PASS / FAIL
            cleaned_data["result"] = (
                cleaned_data["score"]
                .apply(
                    lambda x:
                    "Pass" if x >= 40 else "Fail"
                )
            )

            # GRADE
            def calculate_grade(score):

                if score >= 90:
                    return "A+"

                elif score >= 80:
                    return "A"

                elif score >= 70:
                    return "B"

                elif score >= 60:
                    return "C"

                elif score >= 50:
                    return "D"

                elif score >= 40:
                    return "E"

                else:
                    return "F"

            cleaned_data["grade"] = (
                cleaned_data["score"]
                .apply(calculate_grade)
            )

            # RANK
            cleaned_data["rank"] = (
                cleaned_data["score"]
                .rank(
                    ascending=False,
                    method="min"
                )
                .astype(int)
            )

        cleaned_data = (
            cleaned_data
            .reset_index(drop=True)
        )

        # -------------------------------------------------
        # DISPLAY
        # -------------------------------------------------

        display_data(cleaned_data)

        update_column_list(cleaned_data)

        update_dashboard(cleaned_data)

        final_missing = (
            cleaned_data.isnull().sum().sum()
        )

        removed_rows = (
            original_rows - len(cleaned_data)
        )

        # -------------------------------------------------
        # CLEANING REPORT
        # -------------------------------------------------

        report = ""

        report += (
            "========== CLEANING REPORT ==========\n\n"
        )

        report += (
            f"Rows before cleaning: "
            f"{original_rows}\n"
        )

        report += (
            f"Rows after cleaning: "
            f"{len(cleaned_data)}\n"
        )

        report += (
            f"Rows removed: "
            f"{removed_rows}\n"
        )

        report += (
            f"Duplicates removed: "
            f"{duplicate_count}\n"
        )

        report += (
            f"Missing values before: "
            f"{original_missing}\n"
        )

        report += (
            f"Missing values after: "
            f"{final_missing}\n"
        )

        report += "\nCleaning completed successfully!"

        output_text.delete(
            "1.0",
            tk.END
        )

        output_text.insert(
            tk.END,
            report
        )

        status_label.config(
            text="Data cleaned successfully."
        )

    except Exception as e:

        messagebox.showerror(
            "Cleaning Error",
            str(e)
        )


# =========================================================
# STATISTICS
# =========================================================

def show_statistics():

    global cleaned_data

    if cleaned_data is None:

        messagebox.showwarning(
            "Warning",
            "Please clean the data first."
        )

        return

    column = column_combo.get()

    if not column:

        messagebox.showwarning(
            "Warning",
            "Please select a numeric column."
        )

        return

    if column not in cleaned_data.columns:

        return

    series = cleaned_data[column].dropna()

    if len(series) == 0:

        return

    average = series.mean()
    highest = series.max()
    lowest = series.min()
    median = series.median()
    total = series.sum()
    standard_deviation = series.std()

    result = ""

    result += (
        f"========== STATISTICS: "
        f"{column.upper()} ==========\n\n"
    )

    result += (
        f"Number of values: {len(series)}\n"
    )

    result += (
        f"Average: {average:.2f}\n"
    )

    result += (
        f"Highest: {highest}\n"
    )

    result += (
        f"Lowest: {lowest}\n"
    )

    result += (
        f"Median: {median:.2f}\n"
    )

    result += (
        f"Total: {total:.2f}\n"
    )

    result += (
        f"Standard Deviation: "
        f"{standard_deviation:.2f}\n"
    )

    # Special score information
    if column == "score":

        result += "\n========== SCORE ANALYSIS ==========\n\n"

        if "name" in cleaned_data.columns:

            top_index = (
                cleaned_data["score"]
                .idxmax()
            )

            result += (
                f"Top Scorer: "
                f"{cleaned_data.loc[top_index, 'name']}\n"
            )

        result += (
            f"Above 80: "
            f"{len(series[series > 80])}\n"
        )

        result += (
            f"Passed: "
            f"{len(series[series >= 40])}\n"
        )

        result += (
            f"Failed: "
            f"{len(series[series < 40])}\n"
        )

        pass_percentage = (
            len(series[series >= 40])
            / len(series)
            * 100
        )

        result += (
            f"Pass Percentage: "
            f"{pass_percentage:.2f}%\n"
        )

    output_text.delete(
        "1.0",
        tk.END
    )

    output_text.insert(
        tk.END,
        result
    )


# =========================================================
# SEARCH
# =========================================================

def search_data():

    global cleaned_data

    if cleaned_data is None:

        messagebox.showwarning(
            "Warning",
            "Please clean the data first."
        )

        return

    search_value = search_entry.get().strip()

    if not search_value:

        display_data(cleaned_data)

        return

    mask = cleaned_data.astype(
        str
    ).apply(
        lambda column:
        column.str.contains(
            search_value,
            case=False,
            na=False
        )
    ).any(axis=1)

    result = cleaned_data[mask]

    display_data(result)

    output_text.delete(
        "1.0",
        tk.END
    )

    output_text.insert(
        tk.END,
        f"Search: {search_value}\n\n"
        f"Records found: {len(result)}"
    )


# =========================================================
# RESET SEARCH
# =========================================================

def reset_search():

    if cleaned_data is not None:

        display_data(cleaned_data)

    elif data is not None:

        display_data(data)


# =========================================================
# FILTER
# =========================================================

def filter_data():

    global cleaned_data

    if cleaned_data is None:

        messagebox.showwarning(
            "Warning",
            "Please clean the data first."
        )

        return

    column = column_combo.get()

    if not column:

        messagebox.showwarning(
            "Warning",
            "Select a numeric column."
        )

        return

    try:

        minimum_text = min_entry.get().strip()
        maximum_text = max_entry.get().strip()

        filtered = cleaned_data.copy()

        if minimum_text:

            minimum = float(minimum_text)

            filtered = filtered[
                filtered[column] >= minimum
            ]

        if maximum_text:

            maximum = float(maximum_text)

            filtered = filtered[
                filtered[column] <= maximum
            ]

        display_data(filtered)

        output_text.delete(
            "1.0",
            tk.END
        )

        output_text.insert(
            tk.END,
            f"========== FILTER ==========\n\n"
            f"Column: {column}\n"
            f"Minimum: {minimum_text or 'No limit'}\n"
            f"Maximum: {maximum_text or 'No limit'}\n\n"
            f"Records found: {len(filtered)}"
        )

    except ValueError:

        messagebox.showerror(
            "Invalid Input",
            "Please enter valid numbers."
        )


# =========================================================
# SORT
# =========================================================

def sort_data(ascending=True):

    global cleaned_data

    if cleaned_data is None:

        messagebox.showwarning(
            "Warning",
            "Please clean the data first."
        )

        return

    column = column_combo.get()

    if not column:

        messagebox.showwarning(
            "Warning",
            "Please select a numeric column."
        )

        return

    sorted_data = cleaned_data.sort_values(
        by=column,
        ascending=ascending
    )

    display_data(sorted_data)

    order = (
        "Ascending"
        if ascending
        else
        "Descending"
    )

    output_text.delete(
        "1.0",
        tk.END
    )

    output_text.insert(
        tk.END,
        f"Sorted by {column}\n"
        f"Order: {order}"
    )


# =========================================================
# CITY ANALYSIS
# =========================================================

def city_analysis():

    global cleaned_data

    if cleaned_data is None:

        messagebox.showwarning(
            "Warning",
            "Please clean the data first."
        )

        return

    if (
        "city" not in cleaned_data.columns
        or
        "score" not in cleaned_data.columns
    ):

        messagebox.showwarning(
            "Not Available",
            "This feature requires "
            "'city' and 'score' columns."
        )

        return

    grouped = (
        cleaned_data
        .groupby("city")["score"]
        .agg(
            ["count", "mean", "max", "min"]
        )
        .round(2)
    )

    result = (
        "========== CITY ANALYSIS ==========\n\n"
    )

    for city, row in grouped.iterrows():

        result += (
            f"{city}\n"
            f"  Students: {row['count']}\n"
            f"  Average: {row['mean']}\n"
            f"  Highest: {row['max']}\n"
            f"  Lowest: {row['min']}\n\n"
        )

    output_text.delete(
        "1.0",
        tk.END
    )

    output_text.insert(
        tk.END,
        result
    )


# =========================================================
# SAVE DATA
# =========================================================

def save_data():

    global displayed_data

    if displayed_data is None:

        messagebox.showwarning(
            "Warning",
            "No data available to save."
        )

        return

    file_path = filedialog.asksaveasfilename(
        title="Save CSV",
        defaultextension=".csv",
        filetypes=[
            ("CSV Files", "*.csv")
        ]
    )

    if file_path:

        try:

            displayed_data.to_csv(
                file_path,
                index=False
            )

            messagebox.showinfo(
                "Success",
                "CSV saved successfully!"
            )

            status_label.config(
                text="CSV saved successfully."
            )

        except Exception as e:

            messagebox.showerror(
                "Error",
                str(e)
            )


# =========================================================
# BAR CHART
# =========================================================

def bar_chart():

    if cleaned_data is None:

        messagebox.showwarning(
            "Warning",
            "Please clean the data first."
        )

        return

    column = column_combo.get()

    if not column:

        return

    if "name" in cleaned_data.columns:

        plt.figure(figsize=(10, 6))

        plt.bar(
            cleaned_data["name"].astype(str),
            cleaned_data[column]
        )

        plt.title(
            f"{column} by Person"
        )

        plt.xlabel(
            "Name"
        )

        plt.ylabel(
            column
        )

        plt.xticks(
            rotation=45
        )

        plt.tight_layout()

        plt.savefig(
            "bar_chart.png"
        )

        plt.show()

    else:

        messagebox.showinfo(
            "Chart",
            "Bar chart requires a 'name' column."
        )


# =========================================================
# HISTOGRAM
# =========================================================

def histogram():

    if cleaned_data is None:
        return

    column = column_combo.get()

    if not column:
        return

    plt.figure(figsize=(8, 5))

    plt.hist(
        cleaned_data[column].dropna(),
        bins=10
    )

    plt.title(
        f"Distribution of {column}"
    )

    plt.xlabel(
        column
    )

    plt.ylabel(
        "Frequency"
    )

    plt.tight_layout()

    plt.savefig(
        "histogram.png"
    )

    plt.show()


# =========================================================
# LINE CHART
# =========================================================

def line_chart():

    if cleaned_data is None:
        return

    column = column_combo.get()

    if not column:
        return

    plt.figure(figsize=(9, 5))

    plt.plot(
        cleaned_data[column].reset_index(drop=True)
    )

    plt.title(
        f"Line Chart - {column}"
    )

    plt.xlabel(
        "Record"
    )

    plt.ylabel(
        column
    )

    plt.tight_layout()

    plt.savefig(
        "line_chart.png"
    )

    plt.show()


# =========================================================
# PIE CHART
# =========================================================

def pie_chart():

    if cleaned_data is None:
        return

    column = column_combo.get()

    if not column:
        return

    if column == "score" and "grade" in cleaned_data.columns:

        grade_counts = (
            cleaned_data["grade"]
            .value_counts()
        )

        plt.figure(figsize=(7, 7))

        plt.pie(
            grade_counts.values,
            labels=grade_counts.index,
            autopct="%1.1f%%"
        )

        plt.title(
            "Grade Distribution"
        )

        plt.tight_layout()

        plt.savefig(
            "grade_distribution.png"
        )

        plt.show()

    else:

        messagebox.showinfo(
            "Pie Chart",
            "Pie chart is available for grade "
            "distribution when a score column exists."
        )


# =========================================================
# CITY CHART
# =========================================================

def city_chart():

    if cleaned_data is None:
        return

    if (
        "city" not in cleaned_data.columns
        or
        "score" not in cleaned_data.columns
    ):

        messagebox.showwarning(
            "Not Available",
            "City chart requires city and score columns."
        )

        return

    city_average = (
        cleaned_data
        .groupby("city")["score"]
        .mean()
    )

    plt.figure(figsize=(8, 5))

    plt.bar(
        city_average.index.astype(str),
        city_average.values
    )

    plt.title(
        "Average Score by City"
    )

    plt.xlabel(
        "City"
    )

    plt.ylabel(
        "Average Score"
    )

    plt.xticks(
        rotation=45
    )

    plt.tight_layout()

    plt.savefig(
        "city_chart.png"
    )

    plt.show()


# =========================================================
# CLEANING REPORT
# =========================================================

def cleaning_report():

    global data
    global cleaned_data

    if data is None or cleaned_data is None:

        messagebox.showwarning(
            "Warning",
            "Please choose and clean a CSV first."
        )

        return

    before_rows = len(data)
    after_rows = len(cleaned_data)

    before_missing = (
        data.isnull().sum().sum()
    )

    after_missing = (
        cleaned_data.isnull().sum().sum()
    )

    duplicates = data.duplicated().sum()

    result = ""

    result += (
        "========================================\n"
    )

    result += (
        "          DATA CLEANING REPORT\n"
    )

    result += (
        "========================================\n\n"
    )

    result += (
        f"Rows before cleaning : {before_rows}\n"
    )

    result += (
        f"Rows after cleaning  : {after_rows}\n"
    )

    result += (
        f"Rows removed         : "
        f"{before_rows - after_rows}\n"
    )

    result += (
        f"Duplicate rows       : {duplicates}\n"
    )

    result += (
        f"Missing values before: "
        f"{before_missing}\n"
    )

    result += (
        f"Missing values after : "
        f"{after_missing}\n"
    )

    result += "\nStatus: CLEANING COMPLETED"

    output_text.delete(
        "1.0",
        tk.END
    )

    output_text.insert(
        tk.END,
        result
    )


# =========================================================
# MAIN WINDOW
# =========================================================

root = tk.Tk()

root.title(
    "CSV Data Cleaning & Analysis Dashboard"
)

root.geometry(
    "1350x850"
)

root.minsize(
    1100,
    700
)


# =========================================================
# TITLE
# =========================================================

title = tk.Label(
    root,
    text="CSV DATA CLEANING & ANALYSIS",
    font=("Arial", 22, "bold")
)

title.pack(
    pady=10
)


subtitle = tk.Label(
    root,
    text="Clean • Analyze • Filter • Sort • Visualize",
    font=("Arial", 11)
)

subtitle.pack(
    pady=2
)


# =========================================================
# DASHBOARD
# =========================================================

dashboard = tk.Frame(root)

dashboard.pack(
    fill="x",
    padx=15,
    pady=10
)


def create_card(parent, title, variable):

    frame = tk.Frame(
        parent,
        relief="ridge",
        borderwidth=2
    )

    frame.pack(
        side="left",
        expand=True,
        fill="both",
        padx=5
    )

    tk.Label(
        frame,
        text=title,
        font=("Arial", 10, "bold")
    ).pack(
        pady=5
    )

    label = tk.Label(
        frame,
        textvariable=variable,
        font=("Arial", 18, "bold")
    )

    label.pack(
        pady=5
    )

    return label


rows_value = tk.StringVar(value="0")
columns_value = tk.StringVar(value="0")
missing_value = tk.StringVar(value="0")
duplicate_value = tk.StringVar(value="0")


create_card(
    dashboard,
    "ROWS",
    rows_value
)

create_card(
    dashboard,
    "COLUMNS",
    columns_value
)

create_card(
    dashboard,
    "MISSING VALUES",
    missing_value
)

create_card(
    dashboard,
    "DUPLICATES",
    duplicate_value
)


# =========================================================
# FILE BUTTONS
# =========================================================

file_frame = tk.Frame(root)

file_frame.pack(
    pady=5
)


tk.Button(
    file_frame,
    text="📂 Choose CSV",
    width=18,
    command=choose_file
).grid(
    row=0,
    column=0,
    padx=4
)


tk.Button(
    file_frame,
    text="ℹ Information",
    width=18,
    command=show_info
).grid(
    row=0,
    column=1,
    padx=4
)


tk.Button(
    file_frame,
    text="🧹 Clean Data",
    width=18,
    command=clean_data
).grid(
    row=0,
    column=2,
    padx=4
)


tk.Button(
    file_frame,
    text="📋 Cleaning Report",
    width=18,
    command=cleaning_report
).grid(
    row=0,
    column=3,
    padx=4
)


tk.Button(
    file_frame,
    text="💾 Save CSV",
    width=18,
    command=save_data
).grid(
    row=0,
    column=4,
    padx=4
)


# =========================================================
# FILE LABEL
# =========================================================

file_label = tk.Label(
    root,
    text="No CSV file selected",
    font=("Arial", 9)
)

file_label.pack(
    pady=3
)


# =========================================================
# SEARCH / FILTER FRAME
# =========================================================

control_frame = tk.LabelFrame(
    root,
    text="Search / Filter / Sort",
    padx=10,
    pady=10
)

control_frame.pack(
    fill="x",
    padx=15,
    pady=5
)


# Search

tk.Label(
    control_frame,
    text="Search:"
).grid(
    row=0,
    column=0,
    padx=5
)


search_entry = tk.Entry(
    control_frame,
    width=18
)

search_entry.grid(
    row=0,
    column=1,
    padx=5
)


tk.Button(
    control_frame,
    text="Search",
    command=search_data
).grid(
    row=0,
    column=2,
    padx=5
)


tk.Button(
    control_frame,
    text="Reset",
    command=reset_search
).grid(
    row=0,
    column=3,
    padx=5
)


# Column

tk.Label(
    control_frame,
    text="Numeric Column:"
).grid(
    row=0,
    column=4,
    padx=5
)


column_combo = ttk.Combobox(
    control_frame,
    width=18,
    state="readonly"
)

column_combo.grid(
    row=0,
    column=5,
    padx=5
)


# Minimum

tk.Label(
    control_frame,
    text="Min:"
).grid(
    row=0,
    column=6,
    padx=5
)


min_entry = tk.Entry(
    control_frame,
    width=10
)

min_entry.grid(
    row=0,
    column=7,
    padx=5
)


# Maximum

tk.Label(
    control_frame,
    text="Max:"
).grid(
    row=0,
    column=8,
    padx=5
)


max_entry = tk.Entry(
    control_frame,
    width=10
)

max_entry.grid(
    row=0,
    column=9,
    padx=5
)


tk.Button(
    control_frame,
    text="Filter",
    command=filter_data
).grid(
    row=0,
    column=10,
    padx=5
)


tk.Button(
    control_frame,
    text="Sort ↑",
    command=lambda:
    sort_data(True)
).grid(
    row=0,
    column=11,
    padx=5
)


tk.Button(
    control_frame,
    text="Sort ↓",
    command=lambda:
    sort_data(False)
).grid(
    row=0,
    column=12,
    padx=5
)


# =========================================================
# ANALYSIS BUTTONS
# =========================================================

analysis_frame = tk.LabelFrame(
    root,
    text="Analysis",
    padx=10,
    pady=8
)

analysis_frame.pack(
    fill="x",
    padx=15,
    pady=5
)


tk.Button(
    analysis_frame,
    text="📊 Statistics",
    width=16,
    command=show_statistics
).pack(
    side="left",
    padx=5
)


tk.Button(
    analysis_frame,
    text="🏙 City Analysis",
    width=16,
    command=city_analysis
).pack(
    side="left",
    padx=5
)


tk.Button(
    analysis_frame,
    text="📊 Bar Chart",
    width=16,
    command=bar_chart
).pack(
    side="left",
    padx=5
)


tk.Button(
    analysis_frame,
    text="📉 Histogram",
    width=16,
    command=histogram
).pack(
    side="left",
    padx=5
)


tk.Button(
    analysis_frame,
    text="📈 Line Chart",
    width=16,
    command=line_chart
).pack(
    side="left",
    padx=5
)


tk.Button(
    analysis_frame,
    text="🥧 Grade Chart",
    width=16,
    command=pie_chart
).pack(
    side="left",
    padx=5
)


tk.Button(
    analysis_frame,
    text="🏙 City Chart",
    width=16,
    command=city_chart
).pack(
    side="left",
    padx=5
)


# =========================================================
# DATA TABLE
# =========================================================

table_frame = tk.Frame(root)

table_frame.pack(
    fill="both",
    expand=True,
    padx=15,
    pady=8
)


tree = ttk.Treeview(
    table_frame
)

tree.pack(
    side="left",
    fill="both",
    expand=True
)


vertical_scroll = ttk.Scrollbar(
    table_frame,
    orient="vertical",
    command=tree.yview
)

vertical_scroll.pack(
    side="right",
    fill="y"
)

tree.configure(
    yscrollcommand=vertical_scroll.set
)


horizontal_scroll = ttk.Scrollbar(
    root,
    orient="horizontal",
    command=tree.xview
)

horizontal_scroll.pack(
    fill="x",
    padx=15
)

tree.configure(
    xscrollcommand=horizontal_scroll.set
)


# =========================================================
# OUTPUT
# =========================================================

output_text = tk.Text(
    root,
    height=8,
    font=("Consolas", 10)
)

output_text.pack(
    fill="x",
    padx=15,
    pady=5
)


# =========================================================
# STATUS
# =========================================================

status_label = tk.Label(
    root,
    text="Ready - Choose a CSV file",
    font=("Arial", 10)
)

status_label.pack(
    pady=5
)


# =========================================================
# START APPLICATION
# =========================================================

root.mainloop()