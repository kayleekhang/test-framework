from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from api import API
from probes import Probe
from ui.pages import Page
from ui.selenium import SeleniumWrapper
from websockets_client import WebSocketChannel

if TYPE_CHECKING:
    from builders import ProductBuilder


@dataclass
class Product:
    """A deployed product composed from optional test capabilities."""

    name: str
    ip: str
    product_type: str
    operational_config: dict
    api: API
    pages: dict[str, Page] = field(default_factory=dict)
    probes: dict[str, Probe] = field(default_factory=dict)
    websockets: dict[str, WebSocketChannel] = field(default_factory=dict)
    selenium: SeleniumWrapper | None = None

    @property
    def has_ui(self) -> bool:
        return self.selenium is not None

    def page(self, name: str) -> Page:
        return _named(self.pages, name, "page")

    def probe(self, name: str) -> Probe:
        return _named(self.probes, name, "probe")

    def websocket(self, name: str) -> WebSocketChannel:
        return _named(self.websockets, name, "WebSocket")

    def quit(self) -> None:
        if self.selenium is not None:
            self.selenium.quit()


def display_product_builder() -> ProductBuilder:
    """Python capability definition that replaces display_product.yml."""
    from builders import PageBuilder, ProductBuilder

    dashboard = (
        PageBuilder("dashboard", route="/")
        .button("acknowledge_alert", test_tag="acknowledge-alert")
        .popup("alert_popup", test_tag="alert-popup")
    )
    settings = (
        PageBuilder("settings", route="/settings")
        .button("save", test_tag="save-settings")
        .text("success_message", test_tag="settings-saved-message")
    )
    return (
        ProductBuilder("display")
        .with_api_endpoint(
            "health", method="GET", protocol="http", port=8080, path="/health"
        )
        .with_api_endpoint(
            "alerts", method="GET", protocol="http", port=8080, path="/api/alerts"
        )
        .with_ui(protocol="https", port=8080)
        .with_page(dashboard)
        .with_page(settings)
    )


def backend_product_builder() -> ProductBuilder:
    from builders import ProductBuilder

    return (
        ProductBuilder("backend")
        .with_api_endpoint(
            "health", method="GET", protocol="http", port=8081, path="/health"
        )
        .with_api_endpoint(
            "status", method="GET", protocol="http", port=8081, path="/api/status"
        )
    )


def audio_device_product_builder() -> ProductBuilder:
    from builders import ProductBuilder

    return (
        ProductBuilder("audio_device")
        .with_api_endpoint(
            "health", method="GET", protocol="http", port=8082, path="/health"
        )
        .with_api_endpoint(
            "audio_status",
            method="GET",
            protocol="http",
            port=8082,
            path="/api/audio/status",
        )
        .with_probe(
            "send_test_tone",
            type="gstreamer",
            timeout_seconds=10,
            pipeline="audiotestsrc wave=sine freq=1000 num-buffers=500 ! "
            "audioconvert ! audioresample ! mulawenc ! rtppcmupay ! "
            "udpsink host=127.0.0.1 port=5004",
        )
        .with_probe(
            "receive_audio",
            type="gstreamer",
            timeout_seconds=10,
            pipeline="udpsrc port=5004 caps=application/x-rtp,media=audio,"
            "clock-rate=8000,encoding-name=PCMU,payload=0 ! rtppcmudepay ! "
            "mulawdec ! audioconvert ! fakesink sync=false",
        )
        .with_probe(
            "audio_packets",
            type="wireshark",
            interface="lo0",
            capture_filter="udp port 5004",
            output_path="artifacts/captures/audio_packets.pcapng",
            timeout_seconds=10,
        )
    )


def _named(items: dict, name: str, kind: str):
    if name not in items:
        available = ", ".join(sorted(items)) or "none"
        raise KeyError(f"Unknown {kind} '{name}'. Available {kind}s: {available}")
    return items[name]
