from framework.deploy.base_deployer import LocalDeployer
from framework.deploy.ssh.ssh_deployer import SSHDeployer
from framework.deploy.scp.scp_deployer import SCPDeployer
from framework.deploy.ansible.ansible_deployer import AnsibleDeployer
from framework.deploy.docker.docker_deployer import DockerDeployer
from framework.deploy.kubernetes.k8s_deployer import K8sDeployer
from framework.deploy.package.deb_deployer import DebDeployer
from framework.deploy.package.rpm_deployer import RpmDeployer

class DeployerFactory:
    @staticmethod
    def create(deployer_type: str):
        deployers = {
            "local": LocalDeployer,
            "ssh": SSHDeployer,
            "scp": SCPDeployer,
            "ansible": AnsibleDeployer,
            "docker": DockerDeployer,
            "kubernetes": K8sDeployer,
            "deb": DebDeployer,
            "rpm": RpmDeployer,
        }
        if deployer_type not in deployers:
            raise ValueError(f"Unknown deployer: {deployer_type}")
        return deployers[deployer_type]()
