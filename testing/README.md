# Composable Product Testing

This package builds black-box test objects by composing API, UI, probe, and
WebSocket capabilities. Python builders define what a product type can do.
Operational YAML defines which deployed instances exist.

## Core model

- `Product` is a small container of already-built components.
- `ProductBuilder` defines a reusable product type.
- `PageBuilder` defines a page and its elements in Python.
- `operational_config.yml` supplies instance names, addresses, and overrides.
- `build_products_from_config` applies builders to all configured instances.
- Low-level adapter factories live in `factory.py`.

There is no product factory, page factory, system object, or display capability
YAML.

## Files

```text
testing/
  api.py
  builders.py
  factory.py
  products.py
  probes.py
  websockets_client.py
  configs/
    operational_config.yml
  ui/
    elements.py
    pages.py
    selenium.py
  tests/
```

## Manual product construction

Use a builder directly when a test needs a custom product definition:

```python
from builders import PageBuilder, ProductBuilder

builder = (
    ProductBuilder("display")
    .with_api_endpoint(
        "health",
        method="GET",
        protocol="https",
        port=8443,
        path="/health",
    )
    .with_ui(
        protocol="https",
        port=8080,
        selenium={
            "browser": "chrome",
            "options": {"headless": True},
        },
    )
    .with_page(
        PageBuilder("settings", "/settings")
        .button("save", test_tag="save-settings")
        .text("success", test_tag="settings-saved-message")
    )
    .with_websocket(
        "events",
        protocol="wss",
        port=8080,
        path="/events",
    )
)

product = builder.build(name="p1", ip="10.0.0.1")
```

The resulting addresses and selectors are resolved from the instance:

```text
API:       https://10.0.0.1:8443/health
UI:        https://10.0.0.1:8080/settings
WebSocket: wss://10.0.0.1:8080/events
Selector:  [data-testid="save-settings_p1"]
```

## Reusable product definitions

Standard definitions live in `products.py`:

```python
from products import display_product_builder

builder = display_product_builder()
product = builder.build(name="p2", ip="10.0.0.2")
```

`display_product_builder()` replaces the deleted `display_product.yml`. Add or
remove display pages and elements in that function.

## Operational configuration

Operational YAML describes deployments, not UI capabilities:

```yaml
productTypeOne:
  builder: display
  instances:
    - name: p1
      ip: 10.0.0.1
    - name: p2
      ip: 10.0.0.2
    - name: p3
      ip: 10.0.0.3
```

Build all configured products:

```python
from builders import build_products_from_config
from config import load_product_config
from products import display_product_builder

operations = load_product_config("configs/operational_config.yml")

products = build_products_from_config(
    operations,
    builders={"display": display_product_builder()},
)

p2 = products["productTypeOne"][1]
```

The returned value is a mapping from operational group to a list of products in
YAML order. Prefer finding a product by name when order may change:

```python
p2 = next(
    product
    for product in products["productTypeOne"]
    if product.name == "p2"
)
```

## Building several instances manually

```python
products = display_product_builder().build_many([
    {"name": "p1", "ip": "10.0.0.1"},
    {"name": "p2", "ip": "10.0.0.2"},
    {"name": "p3", "ip": "10.0.0.3"},
])
```

Each product receives independent API endpoints, pages, selector suffixes,
WebSocket channels, and a lazily created Selenium driver.

## Using composed components

```python
response = product.api.request("health")

settings = product.page("settings")
settings.open()
settings.click("save")

events = product.websocket("events")
reply = events.exchange({"command": "status"})

capture = product.probe("audio_packets")
result = capture.capture()
```

## Selenium configuration

Pass Selenium settings to `with_ui`:

```python
.with_ui(
    protocol="https",
    port=8080,
    selenium={
        "browser": "chrome",
        "options": {
            "headless": True,
            "arguments": ["--disable-dev-shm-usage"],
            "page_load_strategy": "normal",
        },
        "timeouts": {
            "implicit_wait_seconds": 0,
            "page_load_seconds": 30,
            "script_seconds": 30,
        },
        "window_size": {"width": 1440, "height": 900},
    },
)
```

The browser starts lazily on the first WebDriver operation.

## Running tests

```bash
pytest
pytest --product display
pytest --requirement REQ-101
pytest --capability CAP-AUDIO-TRANSPORT
pytest --operational-config configs/operational_config.yml
```

## Design rule

Put reusable test capability definitions in Python builders. Put names,
addresses, and deployment-specific overrides in operational YAML.
