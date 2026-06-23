from framework.products.base_product import BaseProduct

class GatewayProduct(BaseProduct):
    def route_message(self, message: str):
        print(f"[GATEWAY] route={message}")
