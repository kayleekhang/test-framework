# Pytest Requirements and Capabilities

Tests use markers for requirement, capability, product, and test-type
traceability.

## Metadata decorators

```python
import pytest

from pytest_metadata import capabilities, products, requirements


@pytest.mark.ui
@pytest.mark.blackbox
@products("display")
@capabilities("CAP-DISPLAY-SETTINGS")
@requirements("REQ-101")
def test_save_button(display_product):
    assert display_product.page("settings").element("save")
```

## Filters

```bash
pytest --requirement REQ-101
pytest --capability CAP-DISPLAY-SETTINGS
pytest --product display
pytest -m ui
pytest -m api
pytest -m probe
pytest -m blackbox
```

Filters can be combined:

```bash
pytest --product display --requirement REQ-101 -m ui
```

## Builder-backed fixtures

The standard fixtures construct products from reusable Python builders:

```python
@pytest.fixture
def display_product():
    return display_product_builder().build(
        name="p1",
        ip="localhost",
    )
```

The generic loader supports manual instance selection:

```python
def test_two_displays(product_loader):
    p1 = product_loader("display", instance_name="p1", ip="10.0.0.1")
    p2 = product_loader("display", instance_name="p2", ip="10.0.0.2")
```

## Operationally configured products

Use the session-scoped `configured_products` fixture to build every instance in
the operational YAML:

```python
def test_configured_displays(configured_products):
    displays = configured_products["productTypeOne"]
    assert [product.name for product in displays] == ["p1", "p2", "p3"]
```

Select a different operational file:

```bash
pytest --operational-config /path/to/site-a.yml
```

## Name-based lookup

Operational groups currently contain lists in YAML order. Avoid relying on an
index when order can change:

```python
def product_named(products, name):
    return next(product for product in products if product.name == name)


p2 = product_named(configured_products["productTypeOne"], "p2")
```

## Traceability guidance

- Mark requirements at the test that verifies them.
- Mark capabilities when tests cross several product types.
- Mark every product type participating in the test.
- Keep deployed instance names in operational YAML, not pytest marker names.
- Use the marker filters for targeted qualification runs.
