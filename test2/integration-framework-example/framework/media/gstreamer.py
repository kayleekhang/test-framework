from dataclasses import dataclass

from framework.config.models import MediaSpec, ProductConfig


@dataclass(frozen=True)
class MediaTransmission:
    sender: ProductConfig
    receiver_ip: str
    spec: MediaSpec


class GStreamer:
    """Small boundary around media send/receive commands."""

    def send(self, sender: ProductConfig, receiver_ip: str, spec: MediaSpec) -> MediaTransmission:
        return MediaTransmission(sender=sender, receiver_ip=receiver_ip, spec=spec)

    def receive(self, receiver: ProductConfig, spec: MediaSpec) -> str:
        return f"{receiver.name}:{spec.protocol}:{spec.media_type}:listening"
