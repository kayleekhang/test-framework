from framework.products.base_product import BaseProduct

class TpmProduct(BaseProduct):
    def quote(self):
        print("[TPM] quote requested")
        return "stub-quote"
