class FrameworkError(Exception):
    pass

class ConfigError(FrameworkError):
    pass

class BuildError(FrameworkError):
    pass
