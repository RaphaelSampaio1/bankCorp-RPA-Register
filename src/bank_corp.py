from playwright.sync_api import sync_playwright, Page


class BankCorp:
    def __init__(self, page: Page):
        self.page = page

    
    def navigate(self, website: str):
        self.page.goto(website, wait_until= "domcontentloaded")


    def login(self, user, password):

        try:
            user_field= self.page.get_by_role("textbox", name="Usuário")
            user_field.click()
            user_field.fill(user)
        except Exception as e:
            print(f"\nOccured and Error: {e}")

        try:
            password_field= self.page.get_by_role("textbox", name="Senha")
            password_field.click()
            password_field.fill(password)
        except Exception as e:
            print("\nOccured and Error in bank_corp: {e}")
        
        try:
            enter_btn= self.page.get_by_role("button", name="ENTRAR")
            enter_btn.click()
        except Exception as e:
            print(f"\nOccured and Error in bank_corp: {e}")


    def register_transactions(self, account_number: str, customer_name: str, amount: int, transfer_type: str):
        """
        Transfer type options: SEPA, MB WAY, SISB, SWIFT
        """
        pass

        
