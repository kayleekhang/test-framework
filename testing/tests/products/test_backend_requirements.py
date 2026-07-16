import pytest

from pytest_metadata import products, requirements


@pytest.mark.api
@pytest.mark.blackbox
@products("backend")
@requirements("REQ-001")
def test_req_001_backend_health_endpoint_exists(backend_product):
    endpoint = backend_product.api.endpoint("health")

    assert endpoint.path == "/health"


@pytest.mark.api
@pytest.mark.blackbox
@products("backend")
@requirements("REQ-002")
def test_req_002_backend_status_endpoint_exists(backend_product):
    endpoint = backend_product.api.endpoint("status")

    assert endpoint.path == "/api/status"
