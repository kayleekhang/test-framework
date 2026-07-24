from __future__ import annotations

import pytest

from builders import build_products_from_config
from config import load_product_config
from products import (
    audio_device_product_builder,
    backend_product_builder,
    display_product_builder,
)
from pytest_metadata import marker_values


def pytest_addoption(parser):
    parser.addoption(
        "--requirement",
        action="append",
        default=[],
        help="Run tests tied to this requirement ID. Can be used multiple times.",
    )
    parser.addoption(
        "--capability",
        action="append",
        default=[],
        help="Run tests tied to this capability ID. Can be used multiple times.",
    )
    parser.addoption(
        "--product",
        action="append",
        default=[],
        help="Run tests tied to this product name. Can be used multiple times.",
    )
    parser.addoption(
        "--operational-config",
        default="configs/operational_config.yml",
        help="Operational YAML describing product groups and instances.",
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "requirements(*ids): requirement IDs covered by the test")
    config.addinivalue_line("markers", "capabilities(*ids): capability IDs covered by the test")
    config.addinivalue_line("markers", "products(*names): product names used by the test")
    config.addinivalue_line("markers", "blackbox: black-box system or product test")
    config.addinivalue_line("markers", "ui: Selenium/UI test")
    config.addinivalue_line("markers", "api: backend/API test")
    config.addinivalue_line("markers", "probe: media/network/tool probe test")


def pytest_collection_modifyitems(config, items):
    requested_requirements = set(config.getoption("--requirement"))
    requested_capabilities = set(config.getoption("--capability"))
    requested_products = set(config.getoption("--product"))
    selected = []
    deselected = []

    for item in items:
        if _matches_requested_metadata(
            item,
            requested_requirements=requested_requirements,
            requested_capabilities=requested_capabilities,
            requested_products=requested_products,
        ):
            selected.append(item)
        else:
            deselected.append(item)

    if deselected:
        config.hook.pytest_deselected(items=deselected)
        items[:] = selected


@pytest.fixture
def product_loader():
    builders = {
        "audio_device": audio_device_product_builder,
        "backend": backend_product_builder,
        "display": display_product_builder,
    }

    def load_product(name: str, driver=None, instance_name: str = "p1", ip: str = "localhost"):
        return builders[name]().build(
            name=instance_name,
            ip=ip,
            driver=driver,
        )

    return load_product


@pytest.fixture(scope="session")
def configured_products(pytestconfig):
    operations = load_product_config(pytestconfig.getoption("--operational-config"))
    return build_products_from_config(
        operations,
        builders={
            "audio_device": audio_device_product_builder(),
            "backend": backend_product_builder(),
            "display": display_product_builder(),
        },
    )


@pytest.fixture
def backend_product(product_loader):
    return product_loader("backend")


@pytest.fixture
def display_product(product_loader):
    return product_loader("display")


@pytest.fixture
def audio_device_product(product_loader):
    return product_loader("audio_device")


def _matches_requested_metadata(
    item: pytest.Item,
    requested_requirements: set[str],
    requested_capabilities: set[str],
    requested_products: set[str],
) -> bool:
    if requested_requirements and not requested_requirements.intersection(
        marker_values(item, "requirements")
    ):
        return False

    if requested_capabilities and not requested_capabilities.intersection(
        marker_values(item, "capabilities")
    ):
        return False

    if requested_products and not requested_products.intersection(
        marker_values(item, "products")
    ):
        return False

    return True
