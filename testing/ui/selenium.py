from __future__ import annotations

from typing import Any, Callable


class SeleniumWrapper:
    """Builds and owns the WebDriver configured for one product."""

    def __init__(
        self,
        base_url: str,
        config: dict[str, Any] | None = None,
        driver: Any = None,
        driver_builder: Callable[[str, Any], Any] | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.config = config or {}
        self.browser = self.config.get("browser", "chrome").lower()
        self.driver = driver
        self.driver_builder = driver_builder
        if self.driver is not None:
            self._configure_driver()

    def __getattr__(self, name: str):
        """Start the browser lazily, then behave like its WebDriver."""
        return getattr(self.get_driver(), name)

    def get_driver(self):
        if self.driver is None:
            self.driver = self._build_driver(self.driver_builder)
            self._configure_driver()
        return self.driver

    def quit(self) -> None:
        if self.driver is not None:
            self.driver.quit()

    def _build_driver(self, driver_builder: Callable[[str, Any], Any] | None):
        options = self._build_options()
        if driver_builder is not None:
            return driver_builder(self.browser, options)

        try:
            from selenium import webdriver
        except ImportError as error:
            raise RuntimeError("Selenium is required to create a UI driver.") from error

        builders = {
            "chrome": webdriver.Chrome,
            "firefox": webdriver.Firefox,
            "edge": webdriver.Edge,
        }
        try:
            builder = builders[self.browser]
        except KeyError as error:
            supported = ", ".join(sorted(builders))
            raise ValueError(
                f"Unsupported Selenium browser '{self.browser}'. Supported: {supported}"
            ) from error
        return builder(options=options)

    def _build_options(self):
        try:
            from selenium.webdriver import ChromeOptions, EdgeOptions, FirefoxOptions
        except ImportError as error:
            raise RuntimeError("Selenium is required to configure a UI driver.") from error

        option_types = {
            "chrome": ChromeOptions,
            "firefox": FirefoxOptions,
            "edge": EdgeOptions,
        }
        try:
            options = option_types[self.browser]()
        except KeyError as error:
            supported = ", ".join(sorted(option_types))
            raise ValueError(
                f"Unsupported Selenium browser '{self.browser}'. Supported: {supported}"
            ) from error

        option_config = self.config.get("options", {})
        for argument in option_config.get("arguments", []):
            options.add_argument(argument)

        if option_config.get("headless"):
            options.add_argument("--headless")

        if "page_load_strategy" in option_config:
            options.page_load_strategy = option_config["page_load_strategy"]

        preferences = option_config.get("preferences", {})
        if preferences:
            if self.browser == "firefox":
                for name, value in preferences.items():
                    options.set_preference(name, value)
            else:
                options.add_experimental_option("prefs", preferences)

        return options

    def _configure_driver(self) -> None:
        timeouts = self.config.get("timeouts", {})
        if "implicit_wait_seconds" in timeouts:
            self.driver.implicitly_wait(timeouts["implicit_wait_seconds"])
        if "page_load_seconds" in timeouts:
            self.driver.set_page_load_timeout(timeouts["page_load_seconds"])
        if "script_seconds" in timeouts:
            self.driver.set_script_timeout(timeouts["script_seconds"])

        window_size = self.config.get("window_size")
        if window_size:
            self.driver.set_window_size(window_size["width"], window_size["height"])
