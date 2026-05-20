from playwright.sync_api import sync_playwright, Page


class BankCorp:
    def __init__(self, page: Page):
        self.page = Page

    
    def navigate(self, website: str):
        self.page.goto(website, wait_until= "domcontentloaded")


    def login(self, user, password):
        pass

    
