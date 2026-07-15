# Page Architecture

This document explains the page design used by the testing framework.

The main idea is:

```text
YAML config describes the UI.
Factories turn config into Python objects.
Page objects expose useful actions.
Elements/adapters hide Selenium details.
Tests call intentful methods instead of raw selectors.
```

## The Layers

```text
Test
  Product
    Page
      Element adapter
        Selector
          Selenium WebDriver
```

Each layer has a different job.

## YAML Config

The YAML file is the source of truth for product UI structure.

Example:

```yaml
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

This says:

- The product UI runs at `http://localhost:3000`.
- The page named `settings` is at `/settings`.
- The page uses the Python page type `settings`.
- The page has a UI element named `save`.
- The `save` element is a button.
- The real DOM should expose `data-testid="display-save-settings"`.

The YAML should answer: "What exists on this product?"

It should not answer: "What workflow should the test perform?"

## Selectors

A selector is the low-level way Selenium finds an element.

This framework supports two selector styles.

Preferred `test_tag` style:

```yaml
save:
  type: button
  test_tag: save-settings
```

With:

```yaml
selector_prefix: display
```

The framework builds this selector:

```css
[data-testid="display-save-settings"]
```

So the UI should have:

```html
<button data-testid="display-save-settings">Save</button>
```

Direct selector style:

```yaml
save:
  type: button
  selector: "#save-settings"
```

Prefer `test_tag` for most test code because it is stable and intentional. Use direct `selector` only when you need to target an existing UI that cannot add `data-testid`.

## Element Adapters

An adapter is a small Python object that wraps Selenium behavior.

In this framework, `UiElement` is the base adapter:

```python
class UiElement:
    def click(self):
        self.clickable().click()

    def text(self) -> str:
        return self.visible().text

    def is_visible(self) -> bool:
        ...
```

Specialized adapters can extend it:

```python
class Button(UiElement):
    pass


class Popup(UiElement):
    def close_with_escape(self):
        self.visible().send_keys("\ue00c")
```

The adapter hides Selenium details like:

- Waiting for presence
- Waiting for visibility
- Waiting for clickability
- Calling `driver.find_element`
- Knowing which selector strategy is used

Tests should not usually talk to Selenium directly. They should talk to adapters through pages.

## Pages

A page represents one route or screen.

The base `Page` class knows how to:

- Open its route
- Find an element by name
- Click an element by name
- Read text from an element by name
- Check visibility by name

Example:

```python
settings = product.page("settings").open()
settings.click("save")
```

That is enough for simple pages.

When a page has real product behavior, create a custom page class:

```python
class SettingsPage(Page):
    def save(self):
        self.click("save")
```

Then tests can use:

```python
settings = product.page("settings").open()
settings.save()
```

The custom page class is not about selectors. Selectors stay in YAML.

The custom page class is about user intent.

## Page Objects vs Config-Only Pages

Start with config-only pages.

```yaml
alerts:
  route: /alerts
  page_type: base
  elements:
    refresh:
      type: button
      test_tag: refresh-alerts
```

Use it generically:

```python
alerts = product.page("alerts").open()
alerts.click("refresh")
```

Add a page object only when tests become repetitive or unclear:

```python
class AlertsPage(Page):
    def refresh(self):
        self.click("refresh")

    def has_empty_state(self) -> bool:
        return self.is_visible("empty_state")
```

This gives you a clean growth path:

```text
Small page: YAML only
Medium page: YAML + simple page class
Complex page: YAML + page class + specialized element adapters
```

## Factories

Factories build the runtime objects from config.

There are three important factories in `product.py`.

## ProductFactory

`ProductFactory` is the top-level builder.

It receives:

```python
driver
config
```

And returns:

```python
Product(api=api, pages=pages, config=config)
```

Conceptually:

```text
ProductFactory
  builds API endpoints
  reads ui.base_url
  reads ui.selector_prefix
  builds every configured page
  returns a Product
```

Usage:

```python
config = load_product_config("configs/display_product.yml")
product = ProductFactory.create(driver, config)
```

The test does not need to know how pages or elements are constructed.

## PageFactory

`PageFactory` chooses which Python page class to use.

The registry looks like this:

```python
PAGE_TYPES = {
    "dashboard": DashboardPage,
    "settings": SettingsPage,
}
```

The YAML chooses the page type:

```yaml
settings:
  route: /settings
  page_type: settings
```

Then the factory does this:

```text
page_type: settings
  -> SettingsPage
```

If the page type is unknown, the framework falls back to the base `Page`.

That means you can add pages quickly without writing a new class:

```yaml
reports:
  route: /reports
  page_type: base
  elements:
    export:
      type: button
      test_tag: export-report
```

## ElementFactory

`ElementFactory` chooses which element adapter to use.

The registry looks like this:

```python
ELEMENT_TYPES = {
    "button": Button,
    "popup": Popup,
    "text": UiElement,
}
```

The YAML chooses the element type:

```yaml
alert_popup:
  type: popup
  test_tag: alert-popup
```

Then the factory does this:

```text
type: popup
  -> Popup
```

If the element type is unknown, the framework falls back to `UiElement`.

## Full Build Flow

When a test starts:

```python
config = load_product_config("configs/display_product.yml")
product = ProductFactory.create(driver, config)
```

The framework does this:

```text
1. Load YAML into a dictionary.
2. ProductFactory reads api.endpoints.
3. ProductFactory creates Endpoint objects.
4. ProductFactory reads ui.pages.
5. For each page, ProductFactory calls PageFactory.
6. PageFactory chooses the page class from page_type.
7. Page initializes its elements.
8. For each element, Page calls ElementFactory.
9. ElementFactory chooses the adapter from type.
10. ElementFactory builds the selector from selector or test_tag.
11. Product is returned with api and pages ready to use.
```

## Runtime Click Flow

When a test calls:

```python
product.page("settings").click("save")
```

This happens:

```text
1. Product returns the settings page.
2. Page finds the element named save.
3. The save element is a Button adapter.
4. Button uses the selector [data-testid="display-save-settings"].
5. Selenium waits until the element is clickable.
6. Selenium clicks the element.
```

The test stays clean:

```python
settings.save()
```

The selector stays in YAML:

```yaml
save:
  type: button
  test_tag: save-settings
```

The Selenium mechanics stay in the adapter:

```python
def click(self):
    self.clickable().click()
```

## Why This Scales

This design lets each concern change independently.

If a selector changes:

```yaml
test_tag: save-settings-v2
```

Only YAML changes.

If a page gets a new workflow:

```python
class SettingsPage(Page):
    def save_and_confirm(self):
        self.click("save")
        self.click("confirm")
```

Only the page object changes.

If a new UI element type appears:

```python
class Toggle(UiElement):
    def enable(self):
        if self.visible().get_attribute("aria-checked") != "true":
            self.click()
```

Only the adapter registry changes:

```python
ELEMENT_TYPES = {
    "button": Button,
    "popup": Popup,
    "text": UiElement,
    "toggle": Toggle,
}
```

Then YAML can use:

```yaml
notifications:
  type: toggle
  test_tag: notifications-toggle
```

## Design Rule

Use this rule when deciding where code belongs:

```text
YAML says what exists.
Factories decide what class to build.
Adapters define how Selenium interacts.
Pages define what the user can do.
Tests verify what should happen.
```

## Further Reading

These are useful sources to share with others when explaining the design:

- [Selenium: Page Object Models](https://www.selenium.dev/documentation/test_practices/encouraged/page_object_models/) explains the Page Object Model and why it helps keep locators and page-specific behavior out of test code.
- [Selenium: Locator Strategies](https://www.selenium.dev/documentation/webdriver/elements/locators/) documents how Selenium finds elements with CSS selectors, IDs, names, XPath, and other locator strategies.
- [Selenium: Test Practices - Locators](https://www.selenium.dev/documentation/test_practices/encouraged/locators/) explains why maintainable locators matter in UI tests.
- [Martin Fowler: Page Object](https://martinfowler.com/bliki/PageObject.html) is the classic Page Object reference and discusses page-facing methods over raw UI mechanics.
- [SeleniumBase on GitHub](https://github.com/seleniumbase/SeleniumBase) is a mature open-source Selenium/pytest project that wraps browser interactions behind a higher-level API.
- [SeleniumBase examples](https://github.com/seleniumbase/SeleniumBase/tree/master/examples) provide open-source examples of pytest-driven Selenium tests.
- [MDN: CSS Selectors](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_selectors) is a good reference for understanding the CSS selector syntax used by Selenium.
- [MDN: CSS Attribute Selectors](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Selectors/Attribute_selectors) documents selectors like `[data-testid="display-save-settings"]`.
- [YAML 1.2.2 Specification](https://yaml.org/spec/1.2.2/) is the official YAML language specification for the config format.
- [Python dataclasses](https://docs.python.org/3/library/dataclasses.html) documents the standard-library feature used for endpoint and API response value objects.
- [HTTPX Clients](https://www.python-httpx.org/advanced/clients/) documents reusable sync clients, connection pooling, and client-level configuration.
- [HTTPX Async Support](https://www.python-httpx.org/async/) documents the async client used for concurrent endpoint execution.
- [Refactoring.Guru: Factory Method](https://refactoring.guru/design-patterns/factory-method) is a readable explanation of the factory pattern used by `ProductFactory`, `PageFactory`, and `ElementFactory`.
- [Refactoring.Guru: Abstract Factory](https://refactoring.guru/design-patterns/abstract-factory) is useful background if the framework later grows into families of related page, element, and product objects.
