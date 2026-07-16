from __future__ import annotations

import shlex
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ProbeResult:
    name: str
    probe_type: str
    command: list[str]
    return_code: int | None
    stdout: str = ""
    stderr: str = ""
    artifacts: list[str] = field(default_factory=list)
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None and self.return_code == 0


class Probe:
    def __init__(self, name: str, config: dict[str, Any]):
        self.name = name
        self.config = config


class GStreamerProbe(Probe):
    executable = "gst-launch-1.0"

    def run_pipeline(self, timeout_seconds: int | None = None) -> ProbeResult:
        pipeline = self.config["pipeline"]
        command = [self.executable, *shlex.split(pipeline)]
        return _run_command(
            name=self.name,
            probe_type="gstreamer",
            command=command,
            timeout_seconds=timeout_seconds or self.config.get("timeout_seconds"),
        )

    def start_pipeline(self) -> subprocess.Popen:
        pipeline = self.config["pipeline"]
        command = [self.executable, *shlex.split(pipeline)]
        _require_executable(self.executable)
        return subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )


class WiresharkProbe(Probe):
    executable = "tshark"

    def capture(self, timeout_seconds: int | None = None) -> ProbeResult:
        output_path = Path(self.config.get("output_path", f"artifacts/captures/{self.name}.pcapng"))
        output_path.parent.mkdir(parents=True, exist_ok=True)

        command = [
            self.executable,
            "-i",
            self.config["interface"],
            "-a",
            f"duration:{timeout_seconds or self.config.get('timeout_seconds', 10)}",
            "-w",
            str(output_path),
        ]

        capture_filter = self.config.get("capture_filter")
        if capture_filter:
            command.extend(["-f", capture_filter])

        result = _run_command(
            name=self.name,
            probe_type="wireshark",
            command=command,
            timeout_seconds=(timeout_seconds or self.config.get("timeout_seconds", 10)) + 5,
        )
        return ProbeResult(
            name=result.name,
            probe_type=result.probe_type,
            command=result.command,
            return_code=result.return_code,
            stdout=result.stdout,
            stderr=result.stderr,
            artifacts=[str(output_path)],
            error=result.error,
        )

    def count_packets(self, capture_path: str | Path, display_filter: str | None = None) -> int:
        command = [self.executable, "-r", str(capture_path), "-T", "fields", "-e", "frame.number"]
        if display_filter:
            command.extend(["-Y", display_filter])

        result = _run_command(
            name=self.name,
            probe_type="wireshark",
            command=command,
            timeout_seconds=self.config.get("timeout_seconds", 10),
        )
        if not result.ok:
            raise RuntimeError(result.error or result.stderr)

        return len([line for line in result.stdout.splitlines() if line.strip()])


class ProbeFactory:
    PROBE_TYPES = {
        "gstreamer": GStreamerProbe,
        "wireshark": WiresharkProbe,
        "tshark": WiresharkProbe,
    }

    @classmethod
    def create(cls, name: str, config: dict[str, Any]) -> Probe:
        probe_type = config["type"]
        probe_cls = cls.PROBE_TYPES.get(probe_type)
        if probe_cls is None:
            raise ValueError(f"Unknown probe type: {probe_type}")
        return probe_cls(name=name, config=config)


def _run_command(
    name: str,
    probe_type: str,
    command: list[str],
    timeout_seconds: int | None,
) -> ProbeResult:
    try:
        _require_executable(command[0])
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
        return ProbeResult(
            name=name,
            probe_type=probe_type,
            command=command,
            return_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )
    except Exception as exc:
        return ProbeResult(
            name=name,
            probe_type=probe_type,
            command=command,
            return_code=None,
            error=str(exc),
        )


def _require_executable(executable: str):
    if shutil.which(executable) is None:
        raise RuntimeError(f"Required executable not found on PATH: {executable}")


def stop_process(process: subprocess.Popen, timeout_seconds: int = 5) -> tuple[str, str]:
    process.terminate()
    try:
        stdout, stderr = process.communicate(timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        process.kill()
        stdout, stderr = process.communicate()
    return stdout or "", stderr or ""


def wait_seconds(duration_seconds: float):
    time.sleep(duration_seconds)
