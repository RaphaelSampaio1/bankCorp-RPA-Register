"""
BankCorp class — handles all web interactions with the banking portal.

Provides methods for navigation, authentication, and filling in transaction
registration forms using Playwright selectors.
"""

from playwright.sync_api import Page


class BankCorp:
    """
    Automates the BankCorp corporate portal.

    Attributes:
        page (Page): Playwright Page instance shared with BrowserManager.
    """

    def __init__(self, page: Page):
        """
        Initialize BankCorp with a Playwright Page instance.

        Args:
            page (Page): An active Playwright page from BrowserManager.
        """
        self.page = page

    def navigate(self, website: str):
        """
        Navigate the browser to the given website URL.

        Args:
            website (str): Full URL of the banking portal.
        """
        self.page.goto(website, wait_until="domcontentloaded")

    def login(self, user: str, password: str):
        """
        Fill in the username and password fields, then click the login button.

        The target site has no real authentication — login always succeeds
        after an 800ms JavaScript delay.

        Args:
            user (str): Username from .env (ConfigData.USER).
            password (str): Password from .env (ConfigData.PASSWORD).
        """
        try:
            user_field = self.page.get_by_role("textbox", name="Usuário")
            user_field.click()
            user_field.fill(user)
        except Exception as e:
            print(f"\nOccured and Error: {e}")

        try:
            password_field = self.page.get_by_role("textbox", name="Senha")
            password_field.click()
            password_field.fill(password)
        except Exception as e:
            print(f"\nOccured and Error in bank_corp: {e}")

        try:
            enter_btn = self.page.get_by_role("button", name="ENTRAR")
            enter_btn.click()
        except Exception as e:
            print(f"\nOccured and Error in bank_corp: {e}")

    def register_transactions(self, transactions: list[dict]):
        """
        Register multiple transactions by filling the form for each one.

        For every transaction dict, fills in the account number, beneficiary
        name, amount, and transfer type, then clicks the "Adicionar" button.

        Transfer type options: SEPA, MB WAY, SIBS, SWIFT.

        Args:
            transactions (list[dict]): List of transaction dicts with keys:
                account_number, customer_name, amount, transaction_type.
        """
        for transaction in transactions:
            try:
                account_field = self.page.get_by_role("textbox", name="Número da Conta")
                account_field.click()
                account_field.fill(transaction["account_number"])

                customer_field = self.page.get_by_role("textbox", name="Nome do Favorecido")
                customer_field.click()
                customer_field.fill(transaction["customer_name"])

                amount_field = self.page.get_by_placeholder("Valor (€)")
                amount_field.click()
                amount_field.fill(str(transaction["amount"]))

                transaction_type = self.page.locator("#tipo")
                transaction_type.select_option(transaction["transaction_type"])

                register_btn = self.page.get_by_role("button", name="Adicionar")
                register_btn.click()

            except Exception as e:
                print(f"\n Error: {e}")
