from __future__ import annotations

from builders import PageBuilder, ProductBuilder, build_products_from_config
from products import display_product_builder
from ui.selenium import SeleniumWrapper


class FakeDriver:
    def __init__(self):
        self.configuration_calls = []

    def implicitly_wait(self, seconds):
        self.configuration_calls.append(("implicit", seconds))

    def set_page_load_timeout(self, seconds):
        self.configuration_calls.append(("page_load", seconds))

    def set_script_timeout(self, seconds):
        self.configuration_calls.append(("script", seconds))

    def set_window_size(self, width, height):
        self.configuration_calls.append(("window", width, height))


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


def test_product_builder_supports_manual_composition():
    builder = (
        ProductBuilder("custom_display")
        .with_api_endpoint(
            "health", method="GET", protocol="https", port=8443, path="/health"
        )
        .with_ui(protocol="https", port=8080)
        .with_page(
            PageBuilder("settings", "/settings").button(
                "save", test_tag="save-settings"
            )
        )
        .with_websocket("events", protocol="wss", port=8080, path="/events")
    )

    product = builder.build(name="p2", ip="10.0.0.2", driver=FakeDriver())

    assert product.name == "p2"
    assert product.api.endpoint("health").url == "https://10.0.0.2:8443/health"
    assert product.page("settings").url == "https://10.0.0.2:8080/settings"
    assert product.page("settings").element("save").selector == (
        '[data-testid="save-settings_p2"]'
    )
    assert product.websocket("events").url == "wss://10.0.0.2:8080/events"


def test_operational_config_builds_many_products_with_one_builder():
    operations = {
        "productTypeOne": {
            "builder": "display",
            "instances": [
                {"name": "p1", "ip": "10.0.0.1"},
                {"name": "p2", "ip": "10.0.0.2"},
                {"name": "p3", "ip": "10.0.0.3"},
            ],
        }
    }

    products = build_products_from_config(
        operations,
        builders={"display": display_product_builder()},
    )

    assert [product.name for product in products["productTypeOne"]] == ["p1", "p2", "p3"]
    assert products["productTypeOne"][2].page("settings").element("save").selector == (
        '[data-testid="save-settings_p3"]'
    )
