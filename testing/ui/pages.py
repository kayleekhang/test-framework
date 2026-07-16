from __future__ import annotations

from typing import Any

from ui.elements import ElementFactory, UiElement, WebDriver


class Page:
    def __init__(
        self,
        driver: WebDriver,
        base_url: str,
        product_prefix: str,
        name: str,
        config: dict[str, Any],
    ):
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.product_prefix = product_prefix
        self.name = name
        self.config = config
        self.route = config["route"]
        self.elements = {
            element_name: ElementFactory.create(
                driver=driver,
                product_prefix=product_prefix,
                name=element_name,
                config=element_config,
            )
            for element_name, element_config in config.get("elements", {}).items()
        }

    @property
    def url(self) -> str:
        return f"{self.base_url}{self.route}"

    def open(self):
        self.driver.get(self.url)
        return self

    def element(self, name: str) -> UiElement:
        return self.elements[name]

    def click(self, name: str):
        self.element(name).click()

    def text(self, name: str) -> str:
        return self.element(name).text()

    def is_visible(self, name: str) -> bool:
        return self.element(name).is_visible()


class DashboardPage(Page):
    def acknowledge_alert(self):
        self.click("acknowledge_alert")

    def alert_is_visible(self) -> bool:
        return self.is_visible("alert_popup")


class SettingsPage(Page):
    def save(self):
        self.click("save")


class PageFactory:
    PAGE_TYPES = {
        "dashboard": DashboardPage,
        "settings": SettingsPage,
    }

    @classmethod
    def create(
        cls,
        driver: WebDriver,
        base_url: str,
        product_prefix: str,
        name: str,
        config: dict[str, Any],
    ) -> Page:
        page_type = config.get("page_type", "base")
        page_cls = cls.PAGE_TYPES.get(page_type, Page)
        return page_cls(
            driver=driver,
            base_url=base_url,
            product_prefix=product_prefix,
            name=name,
            config=config,
        )
