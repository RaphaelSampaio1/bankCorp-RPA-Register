from src.browser import BrowserManager
from src.bank_corp import BankCorp
from src.config import ConfigData



def run_all():
    browser = BrowserManager()
    bank_corp= BankCorp(page= browser.page)
    

    try:
        bank_corp.navigate(website= ConfigData.SITE_URL)

        bank_corp.login(user= ConfigData.USER,
                        password= ConfigData.PASSWORD)
        
    except Exception as e:
        print(f"\nOccured and Error in bank_corp: {e}")

    input("")


if __name__ == "__main__":
    run_all()