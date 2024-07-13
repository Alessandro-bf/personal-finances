import gspread
from google.oauth2.service_account import Credentials

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('personal_finances')

def add_transactions():
    """
    Get transactions from the user and add them to the Google Sheet.
    """
    worksheet = SHEET.worksheet('transactions')
    
    print("Enter a new transaction")
    
    date = input("Enter the date (DD-MM-YYYY): ")
    category = input("Enter the category: ")
    amount = input("Enter the amount: ")
    description = input("Enter the description: ")
    
    transaction = [date, category, amount, description]
    
    worksheet.append_row(transaction)
    print("Transaction added successfully!")

add_transactions()