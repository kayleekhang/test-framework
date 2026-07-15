# Design Rationale

This document explains why the testing framework uses YAML-driven product definitions, factories, page objects, element adapters, and concurrent API execution.

It is written for design reviews: what was recommended, why it was recommended, where the idea comes from, and where the design should evolve.

## Sources Used

The design is based on these references:

- [Selenium: Page Object Models](https://www.selenium.dev/documentation/test_practices/encouraged/page_object_models/) recommends separating tests from page-specific code and locators, and keeping page operations in page objects.
- [Selenium: Locator Strategies](https://www.selenium.dev/documentation/webdriver/elements/locators/) documents the locator strategies Selenium supports.
- [Selenium: Test Practices - Locators](https://www.selenium.dev/documentation/test_practices/encouraged/locators/) explains why test locators should be maintainable.
- [Martin Fowler: Page Object](https://martinfowler.com/bliki/PageObject.html) is the classic Page Object reference and discusses modeling UI behavior behind page-facing methods.
- [SeleniumBase on GitHub](https://github.com/seleniumbase/SeleniumBase) is a large open-source Selenium/pytest framework. It is useful as an example of wrapping raw Selenium calls behind a higher-level testing API.
- [SeleniumBase examples](https://github.com/seleniumbase/SeleniumBase/tree/master/examples) show real pytest/Selenium tests built around higher-level browser actions.
- [MDN: CSS Attribute Selectors](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Selectors/Attribute_selectors) documents the CSS selector form used for `data-testid`.
- [Python dataclasses](https://docs.python.org/3/library/dataclasses.html) supports the small typed value objects used for endpoints and API responses.
- [Python concurrent.futures](https://docs.python.org/3/library/concurrent.futures.html) supports the `ThreadPoolExecutor` approach used for concurrent endpoint calls.
- [HTTPX Async Support](https://www.python-httpx.org/async/) is the likely next step if the API layer grows into a larger async HTTP client.

## Why Page Objects

Selenium's Page Object guidance says the benefit is separation:

```text
tests should not be full of page-specific locators and Selenium mechanics
```

That is why tests should look like this:

```python
settings = product.page("settings").open()
settings.save()
```

Instead of this:

```python
driver.find_element(By.CSS_SELECTOR, '[data-testid="display-save-settings"]').click()
```

The second version works, but it does not scale. If the selector changes, every test that copied it has to change. If the save flow becomes "click save, wait for modal, confirm", every test has to learn that workflow.

With page objects, selector changes stay in YAML and workflow changes stay in the page class.

## Why Element Adapters

An element adapter is a small wrapper around Selenium behavior.

`UiElement`, `Button`, and `Popup` are adapters.

They exist so the framework has one place for:

- Waiting for presence
- Waiting for visibility
- Waiting for clickability
- Clicking
- Reading text
- Handling popups

This is the same general direction as projects like SeleniumBase: raw Selenium is wrapped in a more test-friendly API.

## Why YAML

YAML is being used because this framework has two kinds of data:

- Operational product data
- Test/UI automation data

The UI test config should remain readable, reviewable, and easy to diff.

Example:

```yaml
settings:
  route: /settings
  page_type: settings
  elements:
    save:
      type: button
      test_tag: save-settings
```

This is not behavior. It is structure.

The behavior belongs in Python:

```python
class SettingsPage(Page):
    def save(self):
        self.click("save")
```

## Generic Product vs Product-Specific Data Models

There are two valid designs:

```text
Generic Product
  Product
  Page
  UiElement
```

And:

```text
Product-Specific Models
  DisplayProduct
  DisplaySettingsPage
  DisplayAlertPopup
```

The recommendation is to start generic and add product-specific classes only when behavior justifies it.

## Why Start Generic

The generic model is better early because:

- Most UI elements are buttons, text, popups, inputs, and toggles.
- Most pages can be opened, clicked, and asserted through the same mechanics.
- You can add pages by editing YAML instead of writing new Python classes.
- It avoids creating many empty product classes that only mirror config.
- It keeps the framework extensible while the product set is still changing.

This is why `Product`, `Page`, and `UiElement` are generic.

## When to Add Product-Specific Models

Add product-specific Python classes when the product has behavior, not just data.

Good reasons:

- A product has a domain workflow, such as `acknowledge_alarm()`.
- A page has a multi-step interaction, such as save -> confirm -> wait for toast.
- A UI component is repeated across pages.
- Tests are repeating the same low-level click sequence.
- A product needs custom API behavior.

Example:

```python
class DisplayDashboardPage(Page):
    def acknowledge_alarm(self):
        self.click("acknowledge_alert")
        self.element("alert_popup").visible()
```

Bad reason:

```text
Creating DisplayProduct only because product_type is display.
```

That usually creates classes with no behavior and increases maintenance.

## Operational Config vs Test Config

Your operational config is for running the product.

Your test config is for testing the product.

They can share data, but they should not become the same file.

Recommended flow:

```text
operational_config.yml
  -> derive stable UI routes, enabled features, product instances
  -> generate or merge display_product.yml
  -> ProductFactory creates test objects
```

This keeps the boundary clear:

- Operational config says how the product runs.
- Test config says how tests find and interact with the UI.

## What Can Be Derived from Operational Config

Good candidates to derive:

- `base_url`
- product instance names
- enabled pages
- enabled optional panels
- API host, port, and paths
- feature-dependent elements

Example:

```yaml
ui:
  base_url: http://localhost:3000
  selector_prefix: display
```

Could be derived from:

```yaml
products:
  display:
    host: localhost
    ui_port: 3000
```

## What Should Stay in Test Config

Keep these in test config:

- `test_tag`
- direct Selenium selectors
- element type, such as `button`, `popup`, `text`
- timeout overrides
- page test names
- test-only helper elements

Reason: those are testing concerns, not operational concerns.

The product does not need to operate with `data-testid="display-save-settings"`. The test does.

## Recommended Merge Design

Use a small generation step instead of hand-copying operational values.

```text
1. Load operational config.
2. Load product test template.
3. Fill derived values like host, port, base_url, enabled pages.
4. Keep test selectors from the test template.
5. Write generated test config to an artifact directory.
6. Run tests from the generated config.
```

Example structure:

```text
configs/
  operational/
    security_system.yml
  test_templates/
    display_product.yml
  generated/
    display_product.yml
```

This lets reviewers see what is operational data and what is test-only data.

## Concurrent API Calls

The current `API` class supports concurrent endpoint calls with `ThreadPoolExecutor`.

Example:

```python
results = product.api.request_many(["health", "alerts"], max_workers=2)

assert results["health"].ok
assert results["alerts"].ok
```

Why `ThreadPoolExecutor` first:

- It is in the Python standard library.
- It is simple for I/O-bound HTTP requests.
- It does not force an async test architecture yet.
- It is easy to replace later.

When to move to `httpx.AsyncClient`:

- You need many concurrent endpoint calls.
- You already use async tests.
- You need connection pooling, retries, auth, streaming, or richer HTTP behavior.
- You want one async client shared across API workflows.

## Design Decision Summary

Use this rule in design discussions:

```text
Start generic for structure.
Add product-specific classes for behavior.
Derive from operational config only when the data is operational.
Keep selectors and test tags in test config.
Use ThreadPoolExecutor now for simple concurrent endpoint checks.
Move to httpx.AsyncClient when API testing becomes a first-class async workflow.
```

