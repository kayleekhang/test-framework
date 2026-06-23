from framework.products.base_product import BaseProduct

class NatsProduct(BaseProduct):
    def publish(self, subject: str, message: str):
        print(f"[NATS] {subject}: {message}")
