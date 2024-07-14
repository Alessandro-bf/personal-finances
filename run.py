import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import re

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('personal_finances')

CATEGORIES = {
    "EX": "Expenses",
    "IN": "Investments",
    "EN": "Entertainment",
    "DO": "Donations",
    "SA": "Savings"
}

def valid_date(date):
    """
    Validate date format DD-MM-YYYY and check if it is a valid date.
    """
    try:
        datetime.strptime(date, '%d-%m-%Y')
        return True
    except ValueError:
        return False

def valid_category(category):
    """
    Validate category input (first two letters, case-insensitive)
    """
    return category.upper() in CATEGORIES

def valid_amount(amount):
    """
    Validate amount format to ensure it is a number with two decimals or an integer.
    """
    return bool(re.match(r'^\d+(\.\d{2})?$', amount))

def get_next_transaction_number(worksheet):
    """
    Get the next transaction number by finding the maximum transaction number in the worksheet and adding 1.
    If there are no transactions, start with 1.
    """
    transactions = worksheet.get_all_values()
    if len(transactions) > 1:  # Assuming the first row is the header
        transaction_numbers = [int(row[0]) for row in transactions[1:] if row[0].isdigit()]
        if transaction_numbers:
            return max(transaction_numbers) + 1
    return 1

def add_transactions():
    """
    Get transactions from the user and add them to the Google Sheet.
    Validate the input before adding.
    """
    worksheet = SHEET.worksheet('transactions')
    
    print("Enter a new transaction")
    
    date = input("Enter the date (DD-MM-YYYY): ")
    while not valid_date(date):
        print("Invalid date format or invalid date.") 
        print("Please enter the date in DD-MM-YYYY format.\n")
        date = input("Enter the date (DD-MM-YYYY): ")
    
    print("Enter the first two letters of the category")
    print("e.g., Expenses(EX), Investment(IN), Entertainment(EN), Donation(DO), Savings(SA)\n")
    
    category = input("Enter the category (EX, IN, EN, DO, SA): ")
    while not valid_category(category):
        print("Invalid category. Please enter one of the following: EX, IN, EN, DO, SA")
        print("e.g., Expenses(EX), Investments(IN), Entertainment(EN), Donations(DO), Savings(SA)\n")
        category = input("Enter the category (EX, IN, EN, DO, SA): ")

    amount = input("Enter the amount: ")
    while not valid_amount(amount):
        print("Invalid amount. Please enter a valid number with two decimals.")
        amount = input("Enter the amount: ")

    description = input("Enter the description: ")

    # To obtain the category value from the categories dictionary. 
    category_value = CATEGORIES[category.upper()]

    # Get the next transaction number
    transaction_number = get_next_transaction_number(worksheet) 

    transaction = [transaction_number, date, category_value, float(amount), description]
    
    worksheet.append_row(transaction)
    
    print("Transaction added successfully!")

def delete_transaction(transaction_number):
    """
    Delete a transaction from the Google Sheet using the transaction number.
    """
    worksheet = SHEET.worksheet('transactions')
    transactions = worksheet.get_all_values()

    for trx, row in enumerate(transactions):
        if row[0].isdigit() and int(row[0]) == transaction_number:
            worksheet.delete_rows(trx + 1) 
            print(f"Transaction {transaction_number} deleted successfully!")
            return
    
    print(f"Transaction {transaction_number} not found.")

add_transactions()

transaction_to_delete = int(input("Enter the transaction number to delete: "))
delete_transaction(transaction_to_delete)