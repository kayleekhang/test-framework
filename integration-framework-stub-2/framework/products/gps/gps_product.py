from framework.products.base_product import BaseProduct

class GpsProduct(BaseProduct):
    def publish_position(self, lat: float, lon: float):
        print(f"[GPS] publish position lat={lat}, lon={lon}")
