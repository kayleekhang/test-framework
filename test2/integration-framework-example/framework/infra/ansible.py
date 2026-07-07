from pathlib import Path
from typing import Any


def apply_playbook(inventory_path: Path, playbook_path: Path, extra_vars: dict[str, Any]) -> None:
    """Mock Ansible entrypoint.

    Real code should shell out to ansible-playbook or call the Ansible runner API.
    Tests keep this as a no-op so the framework shape can run without VMs.
    """
    if not inventory_path.exists():
        raise FileNotFoundError(f"Inventory does not exist: {inventory_path}")
    if not playbook_path.exists():
        raise FileNotFoundError(f"Playbook does not exist: {playbook_path}")
