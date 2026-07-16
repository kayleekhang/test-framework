# Pytest Requirements and Capabilities

This framework supports two overlapping ways to organize tests:

```text
Product requirement tests
  verify one product's declared requirements

Capability tests
  verify behavior that can span multiple products
```

Examples:

```text
REQ-001: backend exposes health endpoint
REQ-101: display settings page exposes save action
CAP-HEALTH-MONITORING: every product in the capability exposes health
CAP-AUDIO-TRANSPORT: audio product can send, receive, and monitor audio traffic
```

## Directory Shape

```text
tests/
  products/
    test_backend_requirements.py
    test_display_requirements.py
  capabilities/
    test_cap_audio_transport.py
```

Product tests are usually scoped to one product.

Capability tests may use several products.

## Metadata Decorators

Use metadata decorators from `pytest_metadata.py`:

```python
import pytest

from pytest_metadata import capabilities, products, requirements


@pytest.mark.api
@pytest.mark.blackbox
@products("backend")
@requirements("REQ-001")
def test_req_001_backend_health_endpoint_exists(backend_product):
    assert backend_product.api.endpoint("health").path == "/health"
```

Capability test:

```python
@pytest.mark.api
@pytest.mark.blackbox
@products("audio_device", "backend")
@capabilities("CAP-HEALTH-MONITORING")
@requirements("REQ-001", "REQ-201")
def test_cap_health_monitoring_has_health_endpoint(product_loader):
    backend = product_loader("backend")
    audio_device = product_loader("audio_device")

    assert backend.api.endpoint("health").path == "/health"
    assert audio_device.api.endpoint("health").path == "/health"
```

## Run by Requirement

Run every test tied to one requirement:

```bash
pytest --requirement REQ-001
```

Run tests tied to either of two requirements:

```bash
pytest --requirement REQ-001 --requirement REQ-201
```

## Run by Capability

Run all tests for a capability:

```bash
pytest --capability CAP-HEALTH-MONITORING
```

Run all audio transport capability tests:

```bash
pytest --capability CAP-AUDIO-TRANSPORT
```

## Run by Product

Run all tests tied to one product:

```bash
pytest --product display
```

Run backend and audio-device tests:

```bash
pytest --product backend --product audio_device
```

## Combine Filters

Run display tests for a specific requirement:

```bash
pytest --product display --requirement REQ-101
```

Run backend tests that are part of a capability:

```bash
pytest --product backend --capability CAP-HEALTH-MONITORING
```

Filters are combined with AND across filter types:

```text
--product backend --capability CAP-HEALTH-MONITORING
  means product is backend
  and capability is CAP-HEALTH-MONITORING
```

Multiple values of the same filter are OR:

```text
--requirement REQ-001 --requirement REQ-201
  means REQ-001 or REQ-201
```

## Run by Test Type

The tests also use regular pytest markers:

```bash
pytest -m api
pytest -m ui
pytest -m probe
pytest -m blackbox
```

You can combine marker expressions with metadata filters:

```bash
pytest -m api --capability CAP-HEALTH-MONITORING
```

## Config Overrides

By default, `conftest.py` maps product names to config files:

```python
DEFAULT_PRODUCT_CONFIGS = {
    "audio_device": "configs/audio_device_product.yml",
    "backend": "configs/backend_product.yml",
    "display": "configs/display_product.yml",
}
```

Override a config path:

```bash
pytest --product-config display=/tmp/generated/display_product.yml
```

Set a config root:

```bash
pytest --config-root /opt/blackbox-testing
```

These can be used by Ansible-generated configs on VMs or hardware targets.

## Traceability

The metadata gives you a simple traceability map:

```text
requirement -> tests
capability -> tests
product -> tests
```

Recommended rule:

```text
Every product requirement test gets:
  @products(...)
  @requirements(...)

Every cross-product capability test gets:
  @products(...)
  @capabilities(...)
  @requirements(...) when applicable
```

This lets you answer:

- Which tests cover `REQ-001`?
- Which tests validate `CAP-HEALTH-MONITORING`?
- Which requirements are exercised by display?
- Which capabilities involve multiple products?

