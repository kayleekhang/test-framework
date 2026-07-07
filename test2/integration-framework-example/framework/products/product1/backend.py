from framework.config.models import MediaSpec, ProductConfig
from framework.media.gstreamer import GStreamer, MediaTransmission
from framework.products.base import BackendClient


class Product1Backend(BackendClient):
    def __init__(self, config: ProductConfig, media: GStreamer):
        super().__init__(config, media)

    def send_udp_request(self, receiver_ip: str, count: int = 1) -> MediaTransmission:
        spec = MediaSpec(protocol="udp", media_type="data", count=count)
        return self.send_media(receiver_ip, spec)
