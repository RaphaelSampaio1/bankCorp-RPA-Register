"""
BrowserManager — initializes and manages the Playwright browser lifecycle.

Uses Chromium with a persistent context so login cookies are saved across runs.
"""

from playwright.sync_api import sync_playwright, Page, BrowserContext


class BrowserManager:
    """
    Launches a persistent Chromium browser instance.

    Default parameters:
        - headless: False    (visible browser for development)
        - user_data_dir:     "./data/Cookies" (persistent session storage)

    Attributes:
        playwright: Playwright instance.
        context (BrowserContext): Persistent browser context.
        page (Page): Reusable page (reuses existing tab if available).
    """

    def __init__(self, headless: bool = False, user_data_dir: str = "./data/Cookies"):
        """
        Initialize the browser with a persistent Chromium context.

        Args:
            headless (bool): Whether to run without a visible UI.
            user_data_dir (str): Path to store cookies and session data.
        """
        self.playwright = sync_playwright().start()

        self.context: BrowserContext = self.playwright.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=headless,
            args=["--start-maximized"]
        )

        if self.context.pages:
            self.page: Page = self.context.pages[0]
        else:
            self.page: Page = self.context.new_page()

    def close(self):
        """
        Close the browser context and stop Playwright.
        """
        self.context.close()
        self.playwright.stop()
