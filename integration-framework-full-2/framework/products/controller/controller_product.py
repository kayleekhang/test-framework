from framework.products.base_product import BaseProduct

class ControllerProduct(BaseProduct):
    def command(self, command_name: str):
        print(f"[CONTROLLER] command={command_name}")
