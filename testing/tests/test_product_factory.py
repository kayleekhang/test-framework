from __future__ import annotations

import pytest

from products import ProductFactory
from ui.selenium import SeleniumWrapper


class FakeDriver:
    def __init__(self):
        self.urls = []
        self.quit_called = False
        self.configuration_calls = []

    def get(self, url):
        self.urls.append(url)

    def quit(self):
        self.quit_called = True

    def implicitly_wait(self, seconds):
        self.configuration_calls.append(("implicit", seconds))

    def set_page_load_timeout(self, seconds):
        self.configuration_calls.append(("page_load", seconds))

    def set_script_timeout(self, seconds):
        self.configuration_calls.append(("script", seconds))

    def set_window_size(self, width, height):
        self.configuration_calls.append(("window", width, height))


def _display_capability() -> dict:
    return {
        "product_type": "display",
        "api": {
            "endpoints": {
                "health": {
                    "method": "GET",
                    "protocol": "https",
                    "port": 8443,
                    "path": "/health",
                }
            }
        },
        "ui": {
            "protocol": "https",
            "port": 8080,
            "pages": {
                "settings": {
                    "route": "/settings",
                    "page_type": "settings",
                    "elements": {
                        "save": {"type": "button", "test_tag": "save-settings"}
                    },
                }
            },
        },
        "websockets": {
            "events": {"protocol": "wss", "port": 8080, "path": "/events"}
        },
    }


def _operations() -> dict:
    return {
        "productTypeOne": [
            {"name": "p1", "ip": "10.0.0.1"},
            {"name": "p2", "ip": "10.0.0.2"},
            {"name": "p3", "ip": "10.0.0.3"},
        ]
    }


def test_selenium_wrapper_applies_product_driver_configuration():
    driver = FakeDriver()
    wrapper = SeleniumWrapper(
        base_url="http://display-1/",
        driver=driver,
        config={
            "browser": "chrome",
            "timeouts": {
                "implicit_wait_seconds": 0,
                "page_load_seconds": 30,
                "script_seconds": 15,
            },
            "window_size": {"width": 1440, "height": 900},
        },
    )

    assert wrapper.base_url == "http://display-1"
    assert driver.configuration_calls == [
        ("implicit", 0),
        ("page_load", 30),
        ("script", 15),
        ("window", 1440, 900),
    ]


def test_caller_selects_one_operational_product_by_name():
    product = ProductFactory.create(
        driver=FakeDriver(),
        capability_config=_display_capability(),
        operational_config=_operations(),
        product_group="productTypeOne",
        product_name="p2",
    )

    assert product.name == "p2"
    assert product.ip == "10.0.0.2"
    assert product.api.endpoint("health").url == "https://10.0.0.2:8443/health"
    assert product.page("settings").url == "https://10.0.0.2:8080/settings"
    assert product.page("settings").element("save").selector == (
        '[data-testid="save-settings_p2"]'
    )
    assert product.websocket("events").url == "wss://10.0.0.2:8080/events"


def test_unknown_operational_product_name_is_rejected():
    with pytest.raises(KeyError, match="Unknown product 'missing'"):
        ProductFactory.create(
            capability_config=_display_capability(),
            operational_config=_operations(),
            product_group="productTypeOne",
            product_name="missing",
        )
