# UI Product Testing

This directory contains a small config-driven UI testing layer for Selenium.

Product configuration should live in `.yml` files. Python should load the YAML, build a `Product`, and then let tests interact with pages and elements by name.

```python
config = load_product_config("configs/display_product.yml")
product = ProductFactory.create(driver, config)

dashboard = product.page("dashboard").open()
dashboard.click("acknowledge_alert")
```

`load_product_config()` uses PyYAML when it is installed. If PyYAML is not installed, it falls back to a small mapping-only YAML reader that supports the config style shown in this README.

## Core Model

```text
Product
  api
    endpoints
  pages
    page
      elements
```

- `Product` owns one API object and many pages.
- `API` owns named endpoints.
- `Page` owns named UI elements for one route.
- `UiElement` wraps a Selenium selector and exposes actions like `click()`, `text()`, and `is_visible()`.

## Config Location

Example:

```text
testing/
  product.py
  configs/
    display_product.yml
```

Each product should get its own YAML file:

```text
configs/
  display_product.yml
  camera_product.yml
  admin_console_product.yml
```

## Required YAML Shape

```yaml
product_type: display

api:
  endpoints: {}

ui:
  base_url: http://localhost:3000
  selector_prefix: display
  pages: {}
```

## API Config

Each endpoint needs `protocol`, `host`, `port`, and `path`.

```yaml
api:
  endpoints:
    health:
      protocol: http
      host: localhost
      port: 8080
      path: /health

    alerts:
      protocol: http
      host: localhost
      port: 8080
      path: /api/alerts
      query:
        limit: "10"
```

Usage:

```python
health_url = product.api.endpoint("health").url
```

## UI Config

Each product has a `base_url`, a `selector_prefix`, and one or more pages.

```yaml
ui:
  base_url: http://localhost:3000
  selector_prefix: display

  pages:
    dashboard:
      route: /
      page_type: dashboard
      elements: {}
```

`selector_prefix` is combined with each element's `test_tag`.

This YAML:

```yaml
ui:
  selector_prefix: display
  pages:
    settings:
      elements:
        save:
          type: button
          test_tag: save-settings
```

Creates this Selenium CSS selector:

```css
[data-testid="display-save-settings"]
```

So the UI should have:

```html
<button data-testid="display-save-settings">Save</button>
```

## Element Config

Each element needs a stable name and either `test_tag` or `selector`.

Preferred:

```yaml
save:
  type: button
  test_tag: save-settings
```

Direct selector:

```yaml
save:
  type: button
  selector: "#save-settings"
```

Supported fields:

```yaml
save:
  type: button
  test_tag: save-settings
  selector: "#save-settings"
  by: css selector
  timeout_seconds: 10
```

Element types currently supported:

- `button`
- `popup`
- `text`

Unknown types fall back to the base `UiElement`.

## Adding a UI Element

Add the element under the page's `elements`.

Before:

```yaml
settings:
  route: /settings
  page_type: settings
  elements:
    save:
      type: button
      test_tag: save-settings
```

After adding a cancel button:

```yaml
settings:
  route: /settings
  page_type: settings
  elements:
    save:
      type: button
      test_tag: save-settings

    cancel:
      type: button
      test_tag: cancel-settings
```

Then use it in a test:

```python
settings = product.page("settings").open()
settings.click("cancel")
```

If the page has a custom page class, add a named method:

```python
class SettingsPage(Page):
    def save(self):
        self.click("save")

    def cancel(self):
        self.click("cancel")
```

Then the test becomes:

```python
settings.cancel()
```

## Removing a UI Element

Remove it from the YAML:

```yaml
cancel:
  type: button
  test_tag: cancel-settings
```

Then remove or update any tests that call:

```python
settings.click("cancel")
settings.element("cancel")
settings.cancel()
```

If the custom page class has a method that only exists for that element, remove that method too.

## Adding a Page

Add a new page under `ui.pages`.

```yaml
ui:
  pages:
    alerts:
      route: /alerts
      page_type: base
      elements:
        refresh:
          type: button
          test_tag: refresh-alerts

        empty_state:
          type: text
          test_tag: alerts-empty-state
```

Then use it:

```python
alerts = product.page("alerts").open()
alerts.click("refresh")
assert alerts.is_visible("empty_state")
```

If the page needs behavior beyond generic `click`, `text`, or `is_visible`, create a custom page class:

```python
class AlertsPage(Page):
    def refresh(self):
        self.click("refresh")

    def has_empty_state(self) -> bool:
        return self.is_visible("empty_state")
```

Register it:

```python
class PageFactory:
    PAGE_TYPES = {
        "dashboard": DashboardPage,
        "settings": SettingsPage,
        "alerts": AlertsPage,
    }
```

Then set the YAML:

```yaml
page_type: alerts
```

## Removing a Page

Remove the page from `ui.pages`.

Then remove or update tests that call:

```python
product.page("alerts")
```

If the page had a custom page class and no other YAML config uses it, remove the class and its registry entry from `PageFactory.PAGE_TYPES`.

## Full YAML Example

See [configs/display_product.yml](/Users/kayleekhang/kyle-june-26/test-framework/testing/configs/display_product.yml:1).

```yaml
product_type: display

api:
  endpoints:
    health:
      protocol: http
      host: localhost
      port: 8080
      path: /health

ui:
  base_url: http://localhost:3000
  selector_prefix: display

  pages:
    settings:
      route: /settings
      page_type: settings
      elements:
        save:
          type: button
          test_tag: save-settings
```

## Orchestration Flow

A normal Selenium test run should follow this flow:

```text
1. Start or connect to the application under test.
2. Create a Selenium WebDriver.
3. Load the product .yml file.
4. Build the Product with ProductFactory.
5. Open pages and interact with elements.
6. Assert UI state.
7. Quit the WebDriver.
```

Example:

```python
from pathlib import Path

from selenium import webdriver

from product import ProductFactory, load_product_config


def test_settings_save():
    driver = webdriver.Chrome()
    config = load_product_config(Path("configs/display_product.yml"))
    product = ProductFactory.create(driver, config)

    settings = product.page("settings").open()
    settings.save()

    assert settings.text("success_message") == "Saved"

    driver.quit()
```

With pytest fixtures:

```python
from pathlib import Path

import pytest
from selenium import webdriver

from product import ProductFactory, load_product_config


@pytest.fixture
def driver():
    driver = webdriver.Chrome()
    yield driver
    driver.quit()


@pytest.fixture
def product(driver):
    config = load_product_config(Path("configs/display_product.yml"))
    return ProductFactory.create(driver, config)


def test_dashboard_alert(product):
    dashboard = product.page("dashboard").open()

    assert dashboard.alert_is_visible()

    dashboard.acknowledge_alert()
```

## When to Use YAML vs Python

Put this in YAML:

- Page names
- Routes
- Element names
- Element selectors
- API endpoint addresses
- Timeouts

Put this in Python page classes:

- Multi-step workflows
- Reusable user actions
- Assertions with meaning
- UI behavior that combines several elements

Good test:

```python
dashboard.acknowledge_alert()
```

Good fallback:

```python
dashboard.click("acknowledge_alert")
```

Avoid spreading raw selectors through tests:

```python
driver.find_element(By.CSS_SELECTOR, '[data-testid="display-acknowledge-alert"]').click()
```

Selectors should mostly live in YAML so UI changes are localized.

## Scaling Rule

Start every page as YAML-only.

Add a custom page class only when one of these happens:

- Tests repeat the same sequence of clicks/assertions.
- A workflow has a name in the product domain.
- The page has popups, confirmation flows, or conditional UI.
- Generic `page.click("name")` starts making tests hard to read.

This keeps small products small while still allowing complex products to grow page by page.
