class DummyBrowser:
    def __init__(self):
        self.visited_urls: list[str] = []
        self.clicked: list[str] = []

    def get(self, url: str) -> None:
        self.visited_urls.append(url)

    def click(self, element_name: str) -> None:
        self.clicked.append(element_name)

    def quit(self) -> None:
        pass


class BrowserFactory:
    def chrome(self):
        return BrowserSession(DummyBrowser())


class BrowserSession:
    def __init__(self, browser: DummyBrowser):
        self._browser = browser

    def __enter__(self) -> DummyBrowser:
        return self._browser

    def __exit__(self, exc_type, exc, traceback) -> None:
        self._browser.quit()
