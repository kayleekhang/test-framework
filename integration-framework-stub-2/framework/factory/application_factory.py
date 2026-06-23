from framework.applications.base_application import BaseApplication
from framework.applications.local_binary_application import LocalBinaryApplication
from framework.applications.remote_binary_application import RemoteBinaryApplication
from framework.applications.systemd_application import SystemdApplication
from framework.applications.simulator_application import SimulatorApplication

class ApplicationFactory:
    @staticmethod
    def create(product_name: str, mode: str, app_config, product_settings: dict) -> BaseApplication:
        if mode == "local_binary":
            return LocalBinaryApplication(product_name, app_config, product_settings)

        if mode == "remote_binary":
            return RemoteBinaryApplication(product_name, app_config, product_settings)

        if mode == "systemd":
            return SystemdApplication(product_name, app_config, product_settings)

        if mode == "simulator":
            return SimulatorApplication(product_name, app_config, product_settings)

        raise ValueError(f"Unknown application mode: {mode}")
