from dataclasses import dataclass
from datetime import datetime

@dataclass
class FrameworkEvent:
    source: str
    action: str
    message: str
    timestamp: datetime

    @staticmethod
    def create(source: str, action: str, message: str):
        return FrameworkEvent(source, action, message, datetime.utcnow())
