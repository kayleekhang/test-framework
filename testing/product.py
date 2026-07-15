from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

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


@dataclass(frozen=True)
class Endpoint:
    protocol: str
    host: str
    port: int
    path: str
    method: str = "GET"
    query: dict[str, str] | None = None
    headers: dict[str, str] | None = None
    body: dict[str, Any] | str | bytes | None = None

    @property
    def url(self) -> str:
        query = f"?{urlencode(self.query)}" if self.query else ""
        return f"{self.protocol}://{self.host}:{self.port}{self.path}{query}"


@dataclass(frozen=True)
class APIResponse:
    endpoint_name: str
    url: str
    status_code: int | None
    body: str | None = None
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None and self.status_code is not None and self.status_code < 400


class API:
    def __init__(self, endpoints: dict[str, Endpoint]):
        self.endpoints = endpoints

    def endpoint(self, name: str) -> Endpoint:
        return self.endpoints[name]

    def request(self, name: str, timeout_seconds: int = 10) -> APIResponse:
        endpoint = self.endpoint(name)
        headers = endpoint.headers or {}
        body = self._encode_body(endpoint.body, headers)

        request = Request(
            endpoint.url,
            data=body,
            headers=headers,
            method=endpoint.method.upper(),
        )

        try:
            with urlopen(request, timeout=timeout_seconds) as response:
                response_body = response.read().decode("utf-8", errors="replace")
                return APIResponse(
                    endpoint_name=name,
                    url=endpoint.url,
                    status_code=response.status,
                    body=response_body,
                )
        except Exception as exc:
            return APIResponse(
                endpoint_name=name,
                url=endpoint.url,
                status_code=None,
                error=str(exc),
            )

    def request_many(
        self,
        names: list[str] | None = None,
        max_workers: int = 5,
        timeout_seconds: int = 10,
    ) -> dict[str, APIResponse]:
        endpoint_names = names or list(self.endpoints)
        results: dict[str, APIResponse] = {}

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_name = {
                executor.submit(self.request, name, timeout_seconds): name
                for name in endpoint_names
            }

            for future in as_completed(future_to_name):
                name = future_to_name[future]
                results[name] = future.result()

        return results

    @staticmethod
    def _encode_body(
        body: dict[str, Any] | str | bytes | None,
        headers: dict[str, str],
    ) -> bytes | None:
        if body is None:
            return None

        if isinstance(body, bytes):
            return body

        if isinstance(body, str):
            return body.encode("utf-8")

        headers.setdefault("Content-Type", "application/json")
        return json.dumps(body).encode("utf-8")


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


class Product:
    def __init__(self, api: API, pages: dict[str, Page], config: dict[str, Any]):
        self.api = api
        self.pages = pages
        self.config = config

    def page(self, name: str) -> Page:
        return self.pages[name]


class ProductFactory:
    @staticmethod
    def create(driver: WebDriver, config: dict[str, Any]) -> Product:
        api = API(
            endpoints={
                name: Endpoint(**endpoint_config)
                for name, endpoint_config in config.get("api", {}).get("endpoints", {}).items()
            }
        )

        ui_config = config["ui"]
        product_prefix = ui_config["selector_prefix"]
        base_url = ui_config["base_url"]
        pages = {
            page_name: PageFactory.create(
                driver=driver,
                base_url=base_url,
                product_prefix=product_prefix,
                name=page_name,
                config=page_config,
            )
            for page_name, page_config in ui_config.get("pages", {}).items()
        }

        return Product(api=api, pages=pages, config=config)


def load_product_config(config_path: str | Path) -> dict[str, Any]:
    try:
        import yaml
    except ImportError as exc:
        yaml = None

    with Path(config_path).open("r", encoding="utf-8") as config_file:
        if yaml is not None:
            config = yaml.safe_load(config_file)
        else:
            config = _load_simple_yaml_mapping(config_file.read())

    if not isinstance(config, dict):
        raise ValueError(f"Product config must be a YAML mapping: {config_path}")

    return config


def _load_simple_yaml_mapping(yaml_text: str) -> dict[str, Any]:
    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, root)]

    for line_number, raw_line in enumerate(yaml_text.splitlines(), start=1):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()
        key, separator, raw_value = line.partition(":")

        if not separator:
            raise ValueError(f"Unsupported YAML line {line_number}: {raw_line}")

        while indent <= stack[-1][0]:
            stack.pop()

        parent = stack[-1][1]
        value = raw_value.strip()

        if value:
            parent[key] = _parse_simple_yaml_scalar(value)
            continue

        child: dict[str, Any] = {}
        parent[key] = child
        stack.append((indent, child))

    return root


def _parse_simple_yaml_scalar(value: str) -> Any:
    if value == "{}":
        return {}

    if value in {"true", "false"}:
        return value == "true"

    if value in {"null", "None"}:
        return None

    if value.startswith(("'", '"')) and value.endswith(("'", '"')):
        return value[1:-1]

    try:
        return int(value)
    except ValueError:
        return value
