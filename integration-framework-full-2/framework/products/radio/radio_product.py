from framework.products.base_product import BaseProduct

class RadioProduct(BaseProduct):
    def transmit(self, message: str):
        print(f"[RADIO] transmit={message}")
