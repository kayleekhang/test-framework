from __future__ import annotations

from threading import Barrier

from systems import SystemFactory
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


def _display_config(base_url: str) -> dict:
    return {
        "product_type": "display",
        "api": {"endpoints": {}},
        "ui": {
            "base_url": base_url,
            "selector_prefix": "display",
            "pages": {
                "dashboard": {
                    "route": "/",
                    "page_type": "dashboard",
                    "elements": {},
                }
            },
        },
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
    assert wrapper.browser == "chrome"
    assert driver.configuration_calls == [
        ("implicit", 0),
        ("page_load", 30),
        ("script", 15),
        ("window", 1440, 900),
    ]


def test_system_factory_gives_each_ui_product_its_own_driver_and_url():
    drivers = []

    def driver_factory(group_name, index, config):
        driver = FakeDriver()
        drivers.append(driver)
        return driver

    system = SystemFactory.create(
        {
            "producta": [
                _display_config("http://display-1"),
                _display_config("http://display-2"),
            ]
        },
        driver_factory=driver_factory,
    )

    system.producta.open("dashboard")

    assert len(system.producta) == 2
    assert system.producta[0].selenium.driver is drivers[0]
    assert system.producta[1].selenium.driver is drivers[1]
    assert drivers[0].urls == ["http://display-1/"]
    assert drivers[1].urls == ["http://display-2/"]

    system.quit()
    assert all(driver.quit_called for driver in drivers)


def test_product_group_runs_clicks_concurrently():
    system = SystemFactory.create(
        {
            "producta": [
                _display_config("http://display-1"),
                _display_config("http://display-2"),
            ]
        },
        driver_factory=lambda *args: FakeDriver(),
    )
    rendezvous = Barrier(2, timeout=1)
    clicked = []

    for index, product in enumerate(system.producta):
        def click(element_name, index=index):
            rendezvous.wait()
            clicked.append((index, element_name))
            return product

        product.click = click

    system.producta.click("btn1")

    assert sorted(clicked) == [(0, "btn1"), (1, "btn1")]
