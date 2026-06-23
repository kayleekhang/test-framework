class SSHClient:
    def run(self, host: str, command: str):
        print(f"[SSH] {host}: {command}")
        return 0
