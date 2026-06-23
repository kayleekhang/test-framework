from framework.applications.base_application import Application

class ApplicationFactory:
    @staticmethod
    def create(product_name: str, product_target: str, product_settings: dict, app_config):
        return Application(
            product_name=product_name,
            target=product_target,
            product_settings=product_settings,
            config=app_config,
        )
