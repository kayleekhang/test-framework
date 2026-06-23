from framework.products.base_product import BaseProduct

class CameraProduct(BaseProduct):
    def inject_frame(self, frame_name: str):
        print(f"[CAMERA] frame={frame_name}")
