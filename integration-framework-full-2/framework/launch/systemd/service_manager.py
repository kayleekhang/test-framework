class ServiceManager:
    def start(self, service_name: str):
        print(f"systemctl start {service_name}")
