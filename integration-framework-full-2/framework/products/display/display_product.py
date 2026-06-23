from framework.products.base_product import BaseProduct

class DisplayProduct(BaseProduct):
    def show_alert(self, message: str):
        print(f"[DISPLAY] alert={message}")
