import sqlite3
import tkinter as tk
from tkinter import ttk
import pandas as pd
from get_database import create_or_update_db
import os

class GUI:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("SQL DB Stock Filtering App")
        self.root.configure(bg='#2e2e2e')  # Set a dark background color
        
        def get_table_names(db_file):
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            conn.close()
            t = [table[0] for table in tables]
            return t[0]
        
        def check_db_file():
            current_directory = os.path.dirname(os.path.abspath(__file__))
            for file in os.listdir(current_directory):
                if file.endswith(".db"):
                    self.user_db_name = file
                    self.user_tb_name = get_table_names(file)
                    create_or_update = 'Update Database'
                    return create_or_update
            create_or_update = 'Create Database'
            return create_or_update
        self.bt_text = check_db_file()
       
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Use 'clam' theme for a modern look
        self.style.configure("TLabel", background='#2e2e2e', foreground='white', font=('Arial', 12))
        self.style.configure("TButton", background='#007acc', foreground='white', font=('Arial', 12))
        self.style.configure("TEntry", font=('Arial', 12))
        self.style.configure("Treeview.Heading", background='#007acc', foreground='white', font=('Arial', 12, 'bold'))
        self.style.configure("Treeview", background='#4e4e4e', foreground='white', fieldbackground='#4e4e4e', font=('Arial', 12))
        self.style.map("TButton", background=[('active', '#005f99')])
        
        if self.bt_text == "Create Database":
            self.root.geometry('500x500')
            userdb = ttk.Entry(self.root)
            userdb.insert(0, 'Enter database name...')
            userdb.bind("<FocusIn>", self.clear_on_click)
            usertb = ttk.Entry(self.root)
            usertb.insert(0, 'Enter table name...')
            usertb.bind("<FocusIn>", self.clear_on_click)
            
            self.user_db_name = userdb.get() 
            self.user_tb_name = usertb.get()
            cr_up_button = ttk.Button(self.root, text=self.bt_text, command=lambda: self.create_update_db(db_name=self.user_db_name, table_name=self.user_tb_name, uc='create'), style="TButton")
            cr_up_button.pack(side=tk.LEFT, padx=5, pady=5)
            userdb.pack(side=tk.LEFT, padx=5, pady=5)
            usertb.pack(side=tk.LEFT, padx=5, pady=5)
            self.root.mainloop()
        if check_db_file() == 'Update Database':
            self.root.geometry('1280x600')
            self.init_load_sql()
            self.create_interface()
            self.root.mainloop()

    def sanitize_column_name(self, name):
        return ''.join(c if c.isalnum() else '_' for c in name)

    def create_interface(self):
        # Create a main frame
        main_frame = tk.Frame(self.root, bg='#2e2e2e')
        main_frame.pack(fill=tk.BOTH, expand=1)

        # Create a frame for the Apply Filter button
        button_frame = tk.Frame(main_frame, bg='#2e2e2e')
        button_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        # Apply Filter button
        apply_filter = ttk.Button(button_frame, text="Apply Filter", command=self.apply_filter, style="TButton")
        apply_filter.pack(side=tk.LEFT, padx=5, pady=5)

        cr_up_button = ttk.Button(button_frame, text=self.bt_text, command=lambda: self.create_update_db(db_name=self.user_db_name, table_name=self.user_tb_name, uc='update'), style="TButton")
        cr_up_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        sort_button = ttk.Button(button_frame, text='Sort By Column:', style="TButton", command=lambda: self.sort_by(col=self.col_combo_var.get(), param=self.by_combo_var.get()))
        sort_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        df = pd.read_sql_query(f"SELECT * FROM {self.user_tb_name} LIMIT 1", self.conn)
        options = list(df.columns)

        self.col_combo_var = tk.StringVar()
        self.col_dropdown = ttk.Combobox(button_frame, values=options, textvariable=self.col_combo_var)
        self.col_dropdown.pack(side=tk.LEFT, padx=5, pady=5)
        self.by_combo_var = tk.StringVar()
        self.by_dropdown = ttk.Combobox(button_frame, values=['ASC', 'DESC'], textvariable=self.by_combo_var)
        self.by_dropdown.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Create a canvas
        self.canvas = tk.Canvas(main_frame, bg='#2e2e2e')
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
        self.inner_frame = tk.Frame(self.canvas, bg='#2e2e2e')

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

            lab = ttk.Label(self.inner_frame, text=column, width=width, anchor='w', padding=5)
            lab.grid(column=i, row=0, sticky='nsew', padx=5, pady=5)

            self.cursor.execute(f"SELECT typeof([{column}]) FROM {self.user_tb_name} LIMIT 1")
            column_type = self.cursor.fetchone()[0]
            
            if column_type in ('integer', 'real'):
                entry_frame = tk.Frame(self.inner_frame, bg='#2e2e2e')
                
                # Create the two entries
                min_entry = ttk.Entry(entry_frame, width=int(width/2))
                max_entry = ttk.Entry(entry_frame, width=int(width/2))
                
                # Pack the entries into the frame
                min_entry.pack(side='left', padx=2, pady=5)
                max_entry.pack(side='left', padx=2, pady=5)
                
                min_entry.insert(0, 'Min...')
                min_entry.bind("<FocusIn>", self.clear_on_click)
                max_entry.insert(0, 'Max...')
                max_entry.bind("<FocusIn>", self.clear_on_click)
                # Place the frame in the grid
                entry_frame.grid(column=i, row=1, sticky='nsew', padx=5, pady=5)
                self.filters[column] = {'type': 'range', 'widget': (min_entry, max_entry)}
            else:
                search = ttk.Entry(self.inner_frame, width=width)
                search.grid(column=i, row=1, sticky='nsew', padx=5, pady=5)
                search.insert(0, 'Search by text...')
                search.bind("<FocusIn>", self.clear_on_click)
                self.filters[column] = {'type': 'text', 'widget': search}

        # Create Treeview for results
        self.tree = ttk.Treeview(self.inner_frame, columns=sanitized_columns, show="headings", height=25)
        for col, sanitized_col in zip(column_list, sanitized_columns):
            self.tree.heading(sanitized_col, text=col)
            self.tree.column(sanitized_col, width=column_widths[sanitized_col] * 10)  # Multiply by 10 to convert character width to pixels (approximate)
        self.tree.grid(row=2, column=0, columnspan=len(column_list), sticky='nsew', padx=5, pady=5)

    def init_load_sql(self):
        self.conn = sqlite3.connect(f"{self.user_db_name}")
        self.cursor = self.conn.cursor()
    
    def clear_on_click(self, event):
        event.widget.delete(0, tk.END)
    
    def apply_filter(self):
        conditions = []
        params = []
        for column, filter_info in self.filters.items():
            if filter_info['type'] == 'range':
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

        self.filter_conditions = conditions
        self.filter_params = params

        self.sort_by(self.col_combo_var.get(), self.by_combo_var.get())

    def fetch_and_display_results(self, query, params=None):
        # Clear existing items in the treeview
        for i in self.tree.get_children():
            self.tree.delete(i)

        # Execute the query
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        results = self.cursor.fetchall()

        # Insert new data
        for row in results:
            self.tree.insert("", "end", values=row)

    def create_update_db(self, db_name, table_name, uc):
        create_or_update_db(db_name=db_name, table_name=table_name, update_or_create=uc)

    def sort_by(self, col, param):
        query = f"SELECT * FROM {self.user_tb_name}"
        
        if self.filter_conditions:
            query += " WHERE " + " AND ".join(self.filter_conditions)
        
        if col and param:
            query += f" ORDER BY {col} {param}"
        
        self.fetch_and_display_results(query, self.filter_params)

gui = GUI()
