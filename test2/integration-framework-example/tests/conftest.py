import os
from pathlib import Path

import pytest

from framework.infra.ansible import apply_playbook
from framework.infra.cloudstack import CloudStackEnvironment
from framework.network import PacketCapture
from framework.products import ProductRegistry
from framework.ui.browser import BrowserFactory


def pytest_addoption(parser):
    parser.addoption("--keep-env", action="store_true", help="Leave VMs running after tests")
    parser.addoption("--product-config", default=os.getenv("PRODUCT_CONFIG"), help="Attach to an existing generated environment config")
    parser.addoption("--iterations", type=int, default=1, help="Repeat tests that request the iteration fixture")
    parser.addoption("--requirement", default=None, help="Run tests marked for one requirement id, for example REQ-001")
    parser.addoption("--product", default=None, help="Run tests marked for one product, for example product1")
    parser.addoption("--capability", default=None, help="Run tests marked for one capability, for example send_udp")
    parser.addoption("--suite", default=None, help="Run tests marked for one suite, for example suite1")


def pytest_generate_tests(metafunc):
    if "iteration" in metafunc.fixturenames:
        count = metafunc.config.getoption("--iterations")
        metafunc.parametrize("iteration", range(1, count + 1))


def pytest_collection_modifyitems(config, items):
    filters = {
        "requirement": config.getoption("--requirement"),
        "product": config.getoption("--product"),
        "capability": config.getoption("--capability"),
        "suite": config.getoption("--suite"),
    }
    filters = {name: value for name, value in filters.items() if value}
    if not filters:
        return

    selected = []
    deselected = []
    for item in items:
        if _matches_marker_filters(item, filters):
            selected.append(item)
        else:
            deselected.append(item)

    if deselected:
        config.hook.pytest_deselected(items=deselected)
        items[:] = selected


def _matches_marker_filters(item, filters):
    for marker_name, expected_value in filters.items():
        markers = item.iter_markers(name=marker_name)
        marker_values = {marker.args[0] for marker in markers if marker.args}
        if expected_value not in marker_values:
            return False
    return True


@pytest.fixture(scope="session")
def repo_root():
    return Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def deployed_env(request, repo_root, tmp_path_factory):
    product_config = request.config.getoption("--product-config")

    if product_config:
        env = CloudStackEnvironment.attached_to_config(Path(product_config))
    else:
        env = CloudStackEnvironment.create_from_templates(
            runtime_dir=tmp_path_factory.mktemp("integration-env"),
            product_count=10,
            ui_products={1, 4, 7},
        )
        apply_playbook(
            inventory_path=env.inventory_path,
            playbook_path=repo_root / "ansible" / "playbooks" / "site.yml",
            extra_vars={"env_id": env.env_id},
        )

    yield env

    if not request.config.getoption("--keep-env"):
        env.destroy()


@pytest.fixture(scope="session")
def products(deployed_env):
    return ProductRegistry.from_environment(deployed_env.config)


@pytest.fixture
def traffic_capture():
    return PacketCapture()


@pytest.fixture
def browser():
    with BrowserFactory().chrome() as driver:
        yield driver
