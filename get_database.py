import yfinance as yf
import pandas as pd
from tqdm import tqdm
import logging
import numpy as np
import sqlite3
import os

# Define ANSI escape sequences for colors
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def create_or_update_db(db_name='stock_database.db',table_name="stocks", update_or_create='update'):
    if update_or_create=='update':
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
                    db_name = file
                    tb_name = get_table_names(file)
                    return db_name, tb_name
        db_name, table_name = check_db_file() 
    # Configure logging to suppress warnings and errors
    logging.basicConfig(level=logging.CRITICAL)

    # Read symbols from CSV
    symbols_csv = pd.read_csv("symbols.csv")
    list_of_symbols = symbols_csv["symbol"].tolist()
    str_of_all_symbols = " ".join([symbol.lower() for symbol in list_of_symbols])

    # Initialize DataFrame
    ticker = yf.Ticker("MSFT")
    data = ticker.info
    columns = list(data.keys())
    df = pd.DataFrame(columns=["symbols"] + columns)
    df["symbols"] = list_of_symbols
    tickers = yf.Tickers(str_of_all_symbols)
    #li = list_of_symbols[-10:]  

    for symbol in tqdm(list_of_symbols, desc="\033[94mProcessing symbols\033[0m", ncols=100):
        try:
            data = tickers.tickers[symbol].info
            data_df = pd.DataFrame([data])
            data_df["symbols"] = symbol
            
            # Ensure all columns from data_df are in df
            for column in data_df.columns:
                if column not in df.columns:
                    df[column] = np.nan
            
            # Align data types
            for column in data_df.columns:
                if column in df.columns:
                    if data_df[column].dtype == 'object':
                        df[column] = df[column].astype('object')
                    elif pd.api.types.is_numeric_dtype(data_df[column]):
                        df[column] = pd.to_numeric(df[column], errors='coerce')
            
            # Concatenate the data
            df = pd.concat([df, data_df], ignore_index=True)
            
        except Exception as e:
            if "404" in str(e):
                tqdm.write(f"{Colors.WARNING}Symbol {symbol} not found. Skipping.{Colors.ENDC}")
            else:
                tqdm.write(f"{Colors.FAIL}Error processing {symbol}: {e}{Colors.ENDC}")
    print(f"\033[92mWriting database...\033[0m")
    try:
        conn = sqlite3.connect(db_name)
        df.to_sql(table_name, conn, index=False, if_exists='replace')

        print(f"Successfully created {table_name} in {db_name}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

    finally:
        if conn:
            conn.close()
    print(f"\033[92mWriting to excel...\033[0m")
    df = df.iloc[8856:]
    df.to_excel('stock_database.xlsx', index=False)
    print(f"{Colors.OKGREEN}Data successfully saved to database.xlsx{Colors.ENDC}")


if __name__ == "__main__":
    create_or_update_db()