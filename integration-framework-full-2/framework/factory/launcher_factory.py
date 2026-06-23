from framework.launch.base_launcher import StubLauncher
from framework.launch.process.process_launcher import ProcessLauncher
from framework.launch.systemd.systemd_launcher import SystemdLauncher
from framework.launch.docker.docker_launcher import DockerLauncher
from framework.launch.kubernetes.pod_launcher import PodLauncher

class LauncherFactory:
    @staticmethod
    def create(launcher_type: str):
        launchers = {
            "stub": StubLauncher,
            "process": ProcessLauncher,
            "systemd": SystemdLauncher,
            "docker": DockerLauncher,
            "kubernetes": PodLauncher,
        }
        if launcher_type not in launchers:
            raise ValueError(f"Unknown launcher: {launcher_type}")
        return launchers[launcher_type]()
