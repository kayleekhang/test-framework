from __future__ import annotations

from pathlib import Path

import pytest

from config import load_product_config
from products import ProductFactory
from pytest_metadata import marker_values


DEFAULT_PRODUCT_CONFIGS = {
    "audio_device": "configs/audio_device_product.yml",
    "backend": "configs/backend_product.yml",
    "display": "configs/display_product.yml",
}


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
        "--config-root",
        default=".",
        help="Directory used to resolve product config paths.",
    )
    parser.addoption(
        "--product-config",
        action="append",
        default=[],
        help="Override a product config path as name=path. Can be used multiple times.",
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


@pytest.fixture(scope="session")
def product_configs(pytestconfig) -> dict[str, Path]:
    config_root = Path(pytestconfig.getoption("--config-root"))
    product_configs = {
        name: config_root / path
        for name, path in DEFAULT_PRODUCT_CONFIGS.items()
    }

    for override in pytestconfig.getoption("--product-config"):
        name, separator, path = override.partition("=")
        if not separator:
            raise ValueError(f"--product-config must be name=path, got: {override}")
        product_configs[name] = config_root / path

    return product_configs


@pytest.fixture
def product_loader(product_configs):
    def load_product(name: str, driver=None):
        config = load_product_config(product_configs[name])
        return ProductFactory.create(driver=driver, config=config)

    return load_product


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
