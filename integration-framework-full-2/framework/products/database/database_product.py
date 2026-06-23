from framework.products.base_product import BaseProduct

class DatabaseProduct(BaseProduct):
    def query(self, sql: str):
        print(f"[DB] query={sql}")
        return []
