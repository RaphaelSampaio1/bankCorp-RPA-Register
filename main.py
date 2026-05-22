from src.browser import BrowserManager
from src.bank_corp import BankCorp
from src.config import ConfigData
import src.extract_data


def run_all():
    browser = BrowserManager()
    bank_corp= BankCorp(page= browser.page)

    transactions= src.extract_data.extract_csv_data(r"data\transacoes.csv")
    

    try:
        bank_corp.navigate(website= ConfigData.SITE_URL)

        bank_corp.login(user= ConfigData.USER,
                        password= ConfigData.PASSWORD)
        
        bank_corp.register_transactions(transactions)

    except Exception as e:
        print(f"\nOccured and Error in main.py: {e}")

    input("")


if __name__ == "__main__":
    run_all()