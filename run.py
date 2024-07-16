"""
The program is designed to manage personal finances using Google Sheets.

It allows the user to add and delete transaction, and create monthly reports.
"""

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
    """Validate date format DD/MM/YYYY and check if it is a valid date."""
    try:
        datetime.strptime(date, '%d/%m/%Y')
        return True
    except ValueError:
        return False


def valid_category(category):
    """Validate category input (first two letters, case-insensitive)."""
    return category.upper() in CATEGORIES


def valid_amount(amount):
    """Validate amount format to ensure it's an integer or has two decimals."""
    return bool(re.match(r'^\d+(\.\d{2})?$', amount))


def valid_description(description):
    """Validate that the description is not empty."""
    return bool(description.strip())


def get_next_transaction_number(worksheet):
    """
    Get the next trx number by adding 1 to the maximum trx number recorded.

    If there are no transactions, start with 1.
    """
    transactions = worksheet.get_all_values()
    if len(transactions) > 1:  # Assuming the first row is the header
        transaction_numbers = [
            int(row[0]) for row in transactions[1:] if row[0].isdigit()
        ]
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

    date = input("Enter the date (DD/MM/YYYY): \n")
    while not valid_date(date):
        print("Invalid date format or invalid date.")
        print("Please enter the date in DD/MM/YYYY format.\n")
        date = input("Enter the date (DD/MM/YYYY): \n")

    # Convert date to a datetime object for validation
    date_obj = datetime.strptime(date, '%d/%m/%Y')
    # Format the date back to DD/MM/YYYY
    formatted_date = date_obj.strftime('%d/%m/%Y')

    print("Enter the first two letters of the category")
    print("e.g., Expenses(EX),Investments(IN),Entertainment(EN),"
          "Donations(DO),Savings(SA)\n")

    category = input("Enter the category (EX, IN, EN, DO, SA): \n")
    while not valid_category(category):
        print("Invalid category."
              " Please enter one of the following: EX, IN, EN, DO, SA")
        print("e.g., Expenses(EX),Investments(IN),Entertainment(EN),"
              "Donations(DO),Savings(SA)\n")
        category = input("Enter the category (EX, IN, EN, DO, SA): \n")

    amount = input("Enter the amount: \n")
    while not valid_amount(amount):
        print("Invalid amount. Please enter a valid number with two decimals.")
        amount = input("Enter the amount: \n")

    description = input("Enter the description: \n")
    while not valid_description(description):
        print("Description cannot be empty. Please enter a description.")
        description = input("Enter the description: \n")

    # To obtain the category value from the categories dictionary.
    category_value = CATEGORIES[category.upper()]

    # Get the next transaction number
    transaction_number = get_next_transaction_number(worksheet)

    transaction = [
        transaction_number, formatted_date, category_value,
        float(amount), description
    ]

    worksheet.append_row(transaction)

    print("Transaction added successfully!")


def delete_transaction(transaction_number):
    """Delete a trx from the Google Sheet using the transaction number."""
    worksheet = SHEET.worksheet('transactions')
    transactions = worksheet.get_all_values()

    for trx, row in enumerate(transactions):
        if row[0].isdigit() and int(row[0]) == transaction_number:
            worksheet.delete_rows(trx + 1)
            print(f"Transaction {transaction_number} deleted successfully!")
            return

    print(f"Transaction {transaction_number} not found.")


def show_last_5_transactions():
    """Display the last 5 transactions from the Google Sheet."""
    worksheet = SHEET.worksheet('transactions')
    transactions = worksheet.get_all_values()

    if len(transactions) <= 1:
        print("No transactions available.")
        return

    # Extract the header and the last 5 transactions (excluding header)
    headers = transactions[0]
    last_5_transactions = transactions[-5:]

    if len(transactions) > 5:
        print("\nLast 5 Transactions:")
        print(headers)
        for trx in last_5_transactions:
            print(trx)
    else:
        print("\nLast 5 Transactions:")
        for trx in last_5_transactions:
            print(trx)


def totalize_by_category_month_year():
    """Process transactions to totalize by category, month, and year."""
    worksheet = SHEET.worksheet('transactions')
    transactions = worksheet.get_all_records()

    totals = {}
    for transaction in transactions:
        date_str = transaction['Date']
        category = transaction['Category']
        amount = float(transaction['Amount'])

        # Convert date string to datetime object
        date_obj = datetime.strptime(date_str, '%d/%m/%Y')

        # Create key based on category, month, and year
        key = (category, date_obj.strftime('%Y-%m'))

        if key not in totals:
            totals[key] = 0.0
        totals[key] += amount

    # Prepare data for category_totals Google Sheet
    results = [['Category', 'Year-Month', 'Total Amount']]
    for key, total in totals.items():
        category, month_year = key
        results.append([category, month_year, f"{total:.2f}"])

    # Add results to category_totals Google Sheet
    try:
        category_totals = SHEET.worksheet('category_totals')
    except gspread.WorksheetNotFound:
        category_totals = SHEET.add_worksheet(
            title='category_totals', rows='100', cols='20'
        )

    # Clear existing content in category_totals Google Sheet
    category_totals.clear()

    # Update category_totals Google Sheet with the results
    category_totals.update(results, 'A1')

    print("Monthly totals by category have been stored in the Google Sheet.")


def totalize_by_month_year():
    """Process transactions to totalize by month and year."""
    worksheet = SHEET.worksheet('transactions')
    transactions = worksheet.get_all_records()

    totals = {}
    for transaction in transactions:
        date_str = transaction['Date']
        amount = float(transaction['Amount'])

        # Convert date string to datetime object
        date_obj = datetime.strptime(date_str, '%d/%m/%Y')

        # Create key based on month and year
        key = date_obj.strftime('%Y-%m')

        if key not in totals:
            totals[key] = 0.0
        totals[key] += amount

    # Prepare data for monthly_totals Google Sheet
    results = [['Year-Month', 'Total Amount']]
    for key, total in totals.items():
        results.append([key, f"{total:.2f}"])

    # Add results to monthly_totals Google Sheet
    try:
        monthly_totals = SHEET.worksheet('monthly_totals')
    except gspread.WorksheetNotFound:
        monthly_totals = SHEET.add_worksheet(
            title='monthly_totals', rows='100', cols='20'
        )

    # Clear existing content in monthly_totals Google Sheet
    monthly_totals.clear()

    # Update monthly_totals Google Sheet with the results
    monthly_totals.update(results, 'A1')

    print("Monthly totals by year have been stored in the Google Sheet.")


def main():
    """Display main menu to access the available actions."""
    while True:
        print()
        print("Choose an action:")
        print("1. Add a transaction")
        print("2. Delete a transaction")
        print("3. Show last 5 transactions")
        print("4. Totalize by category, month and year")
        print("5. Totalize by month and year")
        print("6. Exit")
        print()
        print("Important: To see Google Sheets details, "
              "copy the next link in your browser:")
        print("https://docs.google.com/spreadsheets/d/"
              "1KUZxGqBcDwc4gIKezwP4BvFFIS0X57Xou9l9Y5biMwY/edit?usp=sharing")
        print()
        choice = input("Enter your choice (1, 2, 3, 4, 5 or 6): \n")

        if choice == '1':
            add_transactions()
        elif choice == '2':
            transaction_to_delete = int(input(
                "Enter the transaction number to delete: \n"
            ))
            delete_transaction(transaction_to_delete)
        elif choice == '3':
            show_last_5_transactions()
        elif choice == '4':
            totalize_by_category_month_year()
        elif choice == '5':
            totalize_by_month_year()
        elif choice == '6':
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, 4, 5 or 6")


main()
