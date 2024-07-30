import sqlite3
import tkinter as tk
from tkinter import ttk
import pandas as pd
from get_database import create_or_update_db
class GUI:
    def __init__(self) -> None:
        while True:
            user_inp = input("Do you want to create/update your database? (yes or no): ").lower()
            if user_inp == 'yes':
                self.user_db_name = input("What do you want the name of the database to be (without .db): ")
                self.user_tb_name = input("What do you want the name of the table to be: ")
                self.create_update_db(db_name=self.user_db_name,table_name=self.user_tb_name)
                break
            elif user_inp == "no":
                self.user_db_name = "stock_database"    
                self.user_tb_name = 'stocks'
                break
            else:
                print('Sorry! But your answer must be either yes or no')
        self.root = tk.Tk()
        self.root.geometry('1280x600')
        self.root.title("SQL DB Stock Filtering App")
        self.root.configure(bg='grey')
        
        self.init_load_sql()
        self.create_interface()
        self.root.mainloop()

    def sanitize_column_name(self, name):
        return ''.join(c if c.isalnum() else '_' for c in name)

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
        df = pd.read_sql_query(f"SELECT * FROM {self.user_tb_name} LIMIT 1", self.conn)
        column_list = df.columns
        sanitized_columns = [self.sanitize_column_name(col) for col in column_list]

        self.filters = {}  # Dictionary to store filter widgets
        column_widths = {}  # Dictionary to store column widths

        for i, (column, sanitized_col) in enumerate(zip(column_list, sanitized_columns)):
            # Calculate the width based on the column name
            width = max(20, len(column) + 2)  # Minimum width of 20, or longer if the column name is longer
            column_widths[sanitized_col] = width

            lab = tk.Label(self.inner_frame, text=column, width=width, padx=5)
            lab.grid(column=i, row=1, sticky='nsew')
           
            selected_option = tk.StringVar()
           
            # Create the dropdown menu
            self.cursor.execute(f"SELECT DISTINCT [{column}] FROM {self.user_tb_name} WHERE [{column}] IS NOT NULL")
            options = [str(option[0]) for option in self.cursor.fetchall()]
            options.sort()  # Sort options

            if options:
                dropdown = ttk.Combobox(self.inner_frame, textvariable=selected_option, values=options, width=width)
                dropdown.grid(column=i, row=2, sticky='nsew')
                self.filters[column] = {'type': 'dropdown', 'widget': dropdown}
            else:
                tk.Label(self.inner_frame, text="No options available", width=width).grid(column=i, row=2, sticky='nsew')
            
            self.cursor.execute(f"SELECT typeof([{column}]) FROM {self.user_tb_name} LIMIT 1")
            column_type = self.cursor.fetchone()[0]
            
            if column_type in ('integer', 'real'):
                entry_frame = tk.Frame(self.inner_frame)
                
                # Create the two entries
                min_entry = tk.Entry(entry_frame, width=int(width))
                max_entry = tk.Entry(entry_frame, width=int(width))
                
                # Pack the entries into the frame
                min_entry.pack(side='left')
                max_entry.pack(side='left')
                
                min_entry.insert(0, 'Min...')
                min_entry.bind("<FocusIn>", self.clear_on_click)
                max_entry.insert(0, 'Max...')
                max_entry.bind("<FocusIn>", self.clear_on_click)
                # Place the frame in the grid
                entry_frame.grid(column=i, row=3, sticky='nsew')
                self.filters[column] = {'type': 'range', 'widget': (min_entry, max_entry)}
            else:
                search = tk.Entry(self.inner_frame, width=width)
                search.grid(column=i, row=3, sticky='nsew')
                search.insert(0, 'Search by text...')
                search.bind("<FocusIn>", self.clear_on_click)
                self.filters[column] = {'type': 'text', 'widget': search}

        apply_filter = tk.Button(self.inner_frame, text="Apply Filter", background="blue", width=30, foreground='white', command=self.apply_filter)
        apply_filter.grid(row=0, column=0)

        # Create Treeview for results
        self.tree = ttk.Treeview(self.inner_frame, columns=sanitized_columns, show="headings", height=25)
        for col, sanitized_col in zip(column_list, sanitized_columns):
            self.tree.heading(sanitized_col, text=col)
            self.tree.column(sanitized_col, width=column_widths[sanitized_col] * 10)  # Multiply by 10 to convert character width to pixels (approximate)
        self.tree.grid(row=4, column=0, columnspan=len(column_list), sticky='nsew')

    def init_load_sql(self):
        self.conn = sqlite3.connect(f"{self.user_db_name}.db")
        self.cursor = self.conn.cursor()
    
    def clear_on_click(self, event):
        event.widget.delete(0, tk.END)
    
    def apply_filter(self):
        conditions = []
        params = []
        for column, filter_info in self.filters.items():
            if filter_info['type'] == 'dropdown':
                value = filter_info['widget'].get()
                if value:
                    conditions.append(f"{column} = ?")
                    params.append(value)
            elif filter_info['type'] == 'range':
                min_value = filter_info['widget'][0].get()
                max_value = filter_info['widget'][1].get()
                if min_value != 'Min...' and max_value != 'Max...':
                    conditions.append(f"{column} BETWEEN ? AND ?")
                    params.extend([min_value, max_value])
                elif min_value != 'Min...':
                    conditions.append(f"{column} >= ?")
                    params.append(min_value)
                elif max_value != 'Max...':
                    conditions.append(f"{column} <= ?")
                    params.append(max_value)
            elif filter_info['type'] == 'text':
                value = filter_info['widget'].get()
                if value and value != 'Search by text...':
                    conditions.append(f"{column} LIKE ?")
                    params.append(f"%{value}%")

        query = f"SELECT * FROM {self.user_tb_name}"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        self.cursor.execute(query, params)
        results = self.cursor.fetchall()

        # Clear existing items in the treeview
        for i in self.tree.get_children():
            self.tree.delete(i)

        # Insert new data
        for row in results:
            self.tree.insert("", "end", values=row)
    def create_update_db(self,db_name,table_name):
        create_or_update_db(db_name=db_name,table_name=table_name)
gui = GUI()
