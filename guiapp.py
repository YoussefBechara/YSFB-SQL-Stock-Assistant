import pandas as pd
import sqlite3
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pandastable import Table, TableModel

class StockDataFilter:
    def __init__(self, master):
        self.master = master
        self.master.title("Stock Data Filter")
        self.master.geometry("800x600")

        self.conn = None
        self.df = None

        self.create_widgets()

    def create_widgets(self):
        # Frame for file selection
        file_frame = ttk.Frame(self.master, padding="10")
        file_frame.pack(fill=tk.X)

        ttk.Button(file_frame, text="Select Excel File", command=self.load_excel).pack(side=tk.LEFT)
        self.file_label = ttk.Label(file_frame, text="No file selected")
        self.file_label.pack(side=tk.LEFT, padx=10)

        # Frame for filter controls
        filter_frame = ttk.Frame(self.master, padding="10")
        filter_frame.pack(fill=tk.X)

        ttk.Label(filter_frame, text="Filter Column:").pack(side=tk.LEFT)
        self.column_var = tk.StringVar()
        self.column_dropdown = ttk.Combobox(filter_frame, textvariable=self.column_var, state="readonly")
        self.column_dropdown.pack(side=tk.LEFT, padx=5)

        ttk.Label(filter_frame, text="Filter Value:").pack(side=tk.LEFT, padx=5)
        self.filter_value = ttk.Entry(filter_frame)
        self.filter_value.pack(side=tk.LEFT, padx=5)

        ttk.Button(filter_frame, text="Apply Filter", command=self.apply_filter).pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="Reset", command=self.reset_filter).pack(side=tk.LEFT)

        # Frame for data table
        table_frame = ttk.Frame(self.master)
        table_frame.pack(expand=True, fill=tk.BOTH)

        self.table = Table(table_frame, showtoolbar=True, showstatusbar=True)
        self.table.show()

    def load_excel(self):
        try:
            file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
            if file_path:
                self.file_label.config(text=file_path)
                self.df = pd.read_excel(file_path)
                self.create_database()
                self.update_column_dropdown()
                self.display_data(self.df)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load Excel file: {str(e)}")

    def create_database(self):
        try:
            self.conn = sqlite3.connect(":memory:")
            self.df.to_sql("stocks", self.conn, index=False, if_exists="replace")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create database: {str(e)}")

    def update_column_dropdown(self):
        self.column_dropdown['values'] = list(self.df.columns)
        self.column_dropdown.set(self.df.columns[0])

    def apply_filter(self):
        if self.conn is None:
            messagebox.showwarning("Warning", "Please load an Excel file first.")
            return

        column = self.column_var.get()
        value = self.filter_value.get()

        if not column or not value:
            messagebox.showwarning("Warning", "Please select a column and enter a filter value.")
            return

        try:
            query = f"SELECT * FROM stocks WHERE {column} LIKE ?"
            filtered_df = pd.read_sql_query(query, self.conn, params=(f'%{value}%',))
            self.display_data(filtered_df)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply filter: {str(e)}")

    def reset_filter(self):
        if self.df is not None:
            self.display_data(self.df)
            self.filter_value.delete(0, tk.END)

    def display_data(self, df):
        self.table.model = TableModel(dataframe=df)
        self.table.redraw()

if __name__ == "__main__":
    root = tk.Tk()
    app = StockDataFilter(root)
    root.mainloop()