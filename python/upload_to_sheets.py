import psycopg2
import pandas as pd
import gspread
import time
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope) #Path to the credentials file from Google Cloud Console
client = gspread.authorize(creds)

# Open the main spreadsheet
spreadsheet = client.open("Sales Data")

# PostgreSQL connection
conn = psycopg2.connect(
    
    host="localhost",
    database="dbname",
    user="username",
    password="password",
    port="5432"
)

# Views to query
views = {
    "fact_sales": "SELECT * FROM gold.fact_sales;",
    "dim_products": "SELECT * FROM gold.dim_products;",
    "dim_customers": "SELECT * FROM gold.dim_customers;"
}

for sheet_name, query in views.items():
    # Fetch data
    df = pd.read_sql(query, conn)
    df = df.astype(str)

    rows, cols = df.shape
    rows += 1  # include header

    # Try to delete existing worksheet (if exists)
    try:
        existing_worksheet = spreadsheet.worksheet(sheet_name)
        spreadsheet.del_worksheet(existing_worksheet)
        print(f"🗑️  Deleted existing worksheet: {sheet_name}")
        time.sleep(2)  # Pause to let Google Sheets process deletion
    except gspread.exceptions.WorksheetNotFound:
        print(f"➕ No existing worksheet to delete for: {sheet_name}")

    # Create new worksheet
    worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=rows, cols=cols)

    # Upload data
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())
    print(f"✅ Uploaded {sheet_name} to Google Sheets")

print("🎉 All views uploaded successfully!")

