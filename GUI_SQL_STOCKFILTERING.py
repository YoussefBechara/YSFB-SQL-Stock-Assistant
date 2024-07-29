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
            lab.grid(column=i, row=1, sticky='nsew')
           
            selected_option = tk.StringVar()
           
            # Create the dropdown menu
            options = df[column].unique().tolist()
            options = [str(option) for option in options if pd.notna(option)]  # Remove NaN values and convert to strings
            options = list(set(options))  # Remove duplicates
            options.sort()  # Sort options

            if options:
                dropdown = ttk.Combobox(self.inner_frame, textvariable=selected_option, values=options)
                dropdown.grid(column=i, row=2, sticky='nsew')
            else:
                tk.Label(self.inner_frame, text="No options available").grid(column=i, row=2, sticky='nsew')
            
            if df[column].dtype == int or df[column].dtype == float:
                entry_frame = tk.Frame(self.inner_frame)
                
                # Create the two entries
                min_entry = tk.Entry(entry_frame)
                max_entry = tk.Entry(entry_frame)
                
                # Pack the entries into the frame
                min_entry.pack(side='left')
                max_entry.pack(side='left')
                
                min_entry.insert(0, 'Min...')
                min_entry.bind("<FocusIn>", self.clear_on_click)
                max_entry.insert(0, 'Max...')
                max_entry.bind("<FocusIn>", self.clear_on_click)
                # Place the frame in the grid
                entry_frame.grid(column=i, row=3, sticky='nsew')        
            else:
                search = tk.Entry(self.inner_frame)
                search.grid(column=i, row=3, sticky='nsew')
                search.insert(0, 'Search by text...')
                search.bind("<FocusIn>", self.clear_on_click)
        apply_filter = tk.Button(self.inner_frame, text="Apply Filter",background="blue",width=30,foreground='white')
        apply_filter.grid(row=0,column=0)
    def init_load_sql(self):
        conn = sqlite3.connect("stock_database.db")
        cursor = conn.cursor()
        cursor.execute("""SELECT * FROM stock_database""")

    def clear_on_click(self,event):
        event.widget.delete(0, tk.END)
gui = GUI()