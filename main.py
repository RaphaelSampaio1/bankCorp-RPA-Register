"""
BankCorp RPA Register — entry point.

Orchestrates the full automation workflow:
    1. Launch browser (BrowserManager)
    2. Login to the banking portal (BankCorp)
    3. Extract transactions from CSV (extract_data)
    4. Register all transactions into the system (BankCorp)
"""

from src.browser import BrowserManager
from src.bank_corp import BankCorp
from src.config import ConfigData
import src.extract_data


def run_all():
    """
    Main workflow: initialize browser, navigate to site, login,
    extract CSV data, and register each transaction.
    """
    browser = BrowserManager()
    bank_corp = BankCorp(page=browser.page)

    transactions = src.extract_data.extract_csv_data(r"data\transacoes.csv")

    try:
        bank_corp.navigate(website=ConfigData.SITE_URL)

        bank_corp.login(user=ConfigData.USER,
                        password=ConfigData.PASSWORD)

        bank_corp.register_transactions(transactions)

    except Exception as e:
        print(f"\nOccured and Error in main.py: {e}")

    print("Automation Executed Succesfully!")
    input(".")
    browser.close()


if __name__ == "__main__":
    run_all()
