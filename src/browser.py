"""
Browser initialize, using cookies and browser parameters
"""

from playwright.sync_api import sync_playwright, Page, BrowserContext

class BrowserManager:
    """
        DEFAULT BROWSER PARAMETERS:

            - headless -> True
            - (Cookies) -> user_data_dir="./data/Cookies"
        """
    def __init__(self, headless: bool = False, user_data_dir: str = "./data/Cookies"):

        self.playwright = sync_playwright().start()

        self.context: BrowserContext = self.playwright.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=headless,
            args=["--start-maximized"]
        )

        # usa a aba que já existe
        if self.context.pages:
            self.page: Page = self.context.pages[0]
        else:
            self.page: Page = self.context.new_page()

    def close(self):
        """
        Close the BROWSER/PAGE
        """
        self.context.close()
        self.playwright.stop()