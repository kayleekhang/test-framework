from framework.config.models import ProductConfig
from framework.products.base import UiClient


class Product1Ui(UiClient):
    def __init__(self, config: ProductConfig):
        super().__init__(config)

    def start_stream_from_page(self, browser) -> None:
        self.open(browser)
        browser.click("start-stream")
