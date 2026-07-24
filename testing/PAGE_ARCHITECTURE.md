# Page Architecture

Pages use composition:

```text
ProductBuilder
  └── PageBuilder
        └── element definitions
              └── ElementFactory
                    └── UiElement / Button / Popup
```

`PageBuilder` is the public construction interface. `ElementFactory` is a
low-level adapter selector in `factory.py`.

## Defining a page

```python
from builders import PageBuilder

settings = (
    PageBuilder("settings", route="/settings")
    .button("save", test_tag="save-settings")
    .text("success", test_tag="settings-saved-message")
)
```

Attach it to a product definition:

```python
from builders import ProductBuilder

builder = (
    ProductBuilder("display")
    .with_ui(protocol="https", port=8080)
    .with_page(settings)
)
```

## Supported element helpers

```python
page.button("save", test_tag="save-settings")
page.popup("alert", test_tag="alert-popup")
page.text("message", test_tag="status-message")
```

Use `element` for other adapter types or direct selectors:

```python
page.element(
    "legacy_control",
    element_type="text",
    selector="#legacy-control",
)
```

## Instance-specific selectors

A test tag is reusable:

```python
.button("save", test_tag="save-settings")
```

The product instance name is appended when the page is built:

```text
p1 → [data-testid="save-settings_p1"]
p2 → [data-testid="save-settings_p2"]
p3 → [data-testid="save-settings_p3"]
```

This lets one page definition drive many deployed instances.

## URL construction

`ProductBuilder` combines the product IP with the UI protocol and port:

```python
builder.with_ui(protocol="https", port=8080)
product = builder.build(name="p2", ip="10.0.0.2")
```

For a settings route, the page URL becomes:

```text
https://10.0.0.2:8080/settings
```

Operational entries may override `ui_protocol` or `ui_port`.

## Runtime interaction

```python
settings = product.page("settings")
settings.open()
settings.click("save")
assert settings.is_visible("success")
```

`Page` delegates element interaction to its composed element adapters.

## Adding a page

Add it to the appropriate reusable builder in `products.py`:

```python
diagnostics = (
    PageBuilder("diagnostics", "/diagnostics")
    .button("refresh", test_tag="refresh-diagnostics")
)

return (
    ProductBuilder("display")
    .with_ui(protocol="https", port=8080)
    .with_page(diagnostics)
)
```

No YAML or registry entry is required.

## Responsibilities

- `PageBuilder`: declares routes and elements.
- `Page`: performs navigation and delegates interactions.
- `ElementFactory`: selects the concrete element adapter.
- `UiElement`: waits for and interacts with Selenium elements.
- `SeleniumWrapper`: configures and owns the product driver.
