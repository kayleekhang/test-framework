import pytest

from pytest_metadata import products, requirements


@pytest.mark.ui
@pytest.mark.blackbox
@products("display")
@requirements("REQ-101")
def test_req_101_display_settings_page_has_save_button(display_product):
    settings = display_product.page("settings")

    assert settings.element("save").selector == '[data-testid="save-settings"]'


@pytest.mark.ui
@pytest.mark.blackbox
@products("display")
@requirements("REQ-102")
def test_req_102_display_dashboard_has_alert_popup(display_product):
    dashboard = display_product.page("dashboard")

    assert dashboard.element("alert_popup").selector == '[data-testid="alert-popup"]'
