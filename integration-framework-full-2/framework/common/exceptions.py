class FrameworkError(Exception):
    pass

class ConfigError(FrameworkError):
    pass

class BuildError(FrameworkError):
    pass

class DeployError(FrameworkError):
    pass

class LaunchError(FrameworkError):
    pass
