from __future__ import annotations

from typing import Any

try:
    from selenium.webdriver.common.by import By
    from selenium.webdriver.remote.webdriver import WebDriver
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait
except ImportError:
    class By:
        CSS_SELECTOR = "css selector"

    WebDriver = Any
    EC = None
    WebDriverWait = None


def _require_selenium():
    if EC is None or WebDriverWait is None:
        raise RuntimeError("Selenium is required to interact with UI elements.")


class UiElement:
    def __init__(
        self,
        driver: WebDriver,
        name: str,
        selector: str,
        by: str = By.CSS_SELECTOR,
        timeout_seconds: int = 10,
    ):
        self.driver = driver
        self.name = name
        self.by = by
        self.selector = selector
        self.timeout_seconds = timeout_seconds

    def find(self):
        _require_selenium()
        return WebDriverWait(self.driver, self.timeout_seconds).until(
            EC.presence_of_element_located((self.by, self.selector))
        )

    def visible(self):
        _require_selenium()
        return WebDriverWait(self.driver, self.timeout_seconds).until(
            EC.visibility_of_element_located((self.by, self.selector))
        )

    def clickable(self):
        _require_selenium()
        return WebDriverWait(self.driver, self.timeout_seconds).until(
            EC.element_to_be_clickable((self.by, self.selector))
        )

    def click(self):
        self.clickable().click()

    def text(self) -> str:
        return self.visible().text

    def is_visible(self) -> bool:
        try:
            self.visible()
            return True
        except Exception:
            return False


class Button(UiElement):
    pass


class Popup(UiElement):
    def close_with_escape(self):
        self.visible().send_keys("\ue00c")


class ElementFactory:
    ELEMENT_TYPES = {
        "button": Button,
        "popup": Popup,
        "text": UiElement,
    }

    @classmethod
    def create(
        cls,
        driver: WebDriver,
        product_prefix: str,
        name: str,
        config: dict[str, Any],
    ) -> UiElement:
        element_type = config.get("type", "text")
        element_cls = cls.ELEMENT_TYPES.get(element_type, UiElement)
        selector = cls._selector(product_prefix, config)

        return element_cls(
            driver=driver,
            name=name,
            selector=selector,
            by=config.get("by", By.CSS_SELECTOR),
            timeout_seconds=config.get("timeout_seconds", 10),
        )

    @staticmethod
    def _selector(product_prefix: str, config: dict[str, Any]) -> str:
        if "selector" in config:
            return config["selector"]

        if "test_tag" in config:
            return f'[data-testid="{product_prefix}-{config["test_tag"]}"]'

        raise ValueError(f"Element config needs selector or test_tag: {config}")
