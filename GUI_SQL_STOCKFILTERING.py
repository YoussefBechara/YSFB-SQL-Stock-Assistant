import sqlite3
import tkinter as tk
from tkinter import ttk
import pandas as pd

class GUI:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.geometry('1280x600')
        self.root.title("SQL DB Stock Filtering App")
       
        self.create_interface()
        self.root.mainloop()
        # self.init_load_sql()
   
    def create_interface(self):
        def on_option_select(column, selected_option):
            print(f"Selected option for {column}: {selected_option}")

        # Create a main frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=1)

        # Create a canvas
        self.canvas = tk.Canvas(main_frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        # Add a scrollbar to the canvas
        y_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        x_scrollbar = ttk.Scrollbar(self.root, orient=tk.HORIZONTAL, command=self.canvas.xview)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Configure the canvas
        self.canvas.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Create another frame inside the canvas
        self.inner_frame = tk.Frame(self.canvas)

        # Add that frame to a window in the canvas
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        # Add the labels to the inner frame
        df = pd.read_excel("stock_database.xlsx")
        column_list = df.columns

        for i, column in enumerate(column_list):
            lab = tk.Label(self.inner_frame, text=column, width=20, padx=5)
            lab.grid(column=i, row=0, sticky='nsew')
           
            selected_option = tk.StringVar()
           
            # Create the dropdown menu
            options = df[column].unique().tolist()
            options = [str(option) for option in options if pd.notna(option)]  # Remove NaN values and convert to strings
            options = list(set(options))  # Remove duplicates
            options.sort()  # Sort options

            if options:
                dropdown = ttk.Combobox(self.inner_frame, textvariable=selected_option, values=options)
                dropdown.grid(column=i, row=1, sticky='nsew')
           
                # Add a button to display the selected option
                show_button = tk.Button(self.inner_frame, text="Show Selection", 
                                        command=lambda col=column, opt=selected_option: on_option_select(col, opt.get()))
                show_button.grid(column=i, row=2, sticky='nsew')
            else:
                tk.Label(self.inner_frame, text="No options available").grid(column=i, row=1, sticky='nsew')

    def init_load_sql(self):
        conn = sqlite3.connect("stock_database.db")
        cursor = conn.cursor()
        cursor.execute("""SELECT * FROM stock_database""")

gui = GUI()