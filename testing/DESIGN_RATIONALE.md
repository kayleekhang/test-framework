# Design Rationale

## Why composition

Products may expose different combinations of HTTP endpoints, pages, probes,
and WebSocket channels. Inheritance creates a growing product-class hierarchy.
Composition lets a builder assemble only the components that a deployed product
supports.

`Product` therefore contains components but does not implement
product-type-specific behavior.

## Why builders

Builders provide readable Python definitions while keeping construction details
in one place:

```python
ProductBuilder("display")
    .with_api_endpoint(...)
    .with_ui(...)
    .with_page(...)
    .with_websocket(...)
```

They support both workflows:

- Manual construction for focused tests.
- Repeated construction from operational YAML.

## Why capabilities are Python

Pages, elements, and product capabilities are test code. Keeping them in Python:

- Provides editor completion and refactoring support.
- Avoids maintaining YAML schemas for object behavior.
- Makes reusable page definitions explicit.
- Allows custom builders without adding registries or subclasses.

`display_product_builder()` replaces `display_product.yml`.

## Why operations remain YAML

Deployment data changes independently of test capabilities. Operational YAML is
appropriate for:

- Instance names
- IP addresses or hostnames
- Product counts
- Builder selection
- Per-instance protocol or port overrides

It should not contain page objects, selectors, Selenium behavior, or API
request logic.

## Manual and configured construction

Manual:

```python
product = display_product_builder().build(
    name="p1",
    ip="10.0.0.1",
)
```

Configured:

```python
products = build_products_from_config(
    operations,
    builders={"display": display_product_builder()},
)
```

The caller supplies the available builders. The configuration selects among
them by name.

## Why product names suffix test tags

One capability definition may represent several UI instances rendered in the
same environment:

```text
save-settings_p1
save-settings_p2
save-settings_p3
```

The reusable definition contains only `save-settings`; construction appends the
selected operational instance name.

Names are more stable than positional suffixes generated from list order.

## Why low-level factories remain

Factories are still useful where a configuration value selects an adapter:

- `button` selects `Button`
- `popup` selects `Popup`
- `gstreamer` selects a GStreamer probe
- `wireshark` selects a packet capture probe

These adapter factories live together in `factory.py`. Product and page
construction use builders instead.

## Why Selenium belongs to each product

Every UI product may need a separate browser session and base URL.
`SeleniumWrapper` is composed into one product and owns:

- Browser selection
- Browser options
- Timeouts
- Window size
- Lazy driver creation
- Driver shutdown

Pages receive that wrapper as their WebDriver.

## Why addresses resolve during construction

API, UI, and WebSocket addresses are calculated once from the operational IP.
Pages are not mutated after construction. This keeps every component of a
product consistent:

```text
API host       ┐
UI base URL    ├── selected operational IP
WebSocket host ┘
```

## Concurrency

The framework no longer contains a system orchestration abstraction. Callers
can use pytest parallelization, threads, or asyncio when simultaneous operation
is required. Products remain independent and can safely own separate drivers.
