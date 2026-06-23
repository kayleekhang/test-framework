from dataclasses import dataclass
from pathlib import Path

@dataclass
class OperationResult:
    ok: bool
    name: str
    message: str
    artifact: Path | None = None
