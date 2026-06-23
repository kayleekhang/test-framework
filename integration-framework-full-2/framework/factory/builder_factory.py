from framework.build.base_builder import StubBuilder
from framework.build.cargo.cargo_builder import CargoBuilder
from framework.build.cmake.cmake_builder import CMakeBuilder
from framework.build.yocto.yocto_builder import YoctoBuilder
from framework.build.docker.docker_builder import DockerBuilder
from framework.build.package.deb_builder import DebBuilder
from framework.build.package.rpm_builder import RpmBuilder
from framework.build.package.tar_builder import TarBuilder

class BuilderFactory:
    @staticmethod
    def create(builder_type: str):
        builders = {
            "stub": StubBuilder,
            "cargo": CargoBuilder,
            "cmake": CMakeBuilder,
            "yocto": YoctoBuilder,
            "docker": DockerBuilder,
            "deb": DebBuilder,
            "rpm": RpmBuilder,
            "tar": TarBuilder,
        }
        if builder_type not in builders:
            raise ValueError(f"Unknown builder: {builder_type}")
        return builders[builder_type]()
