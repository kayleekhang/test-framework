from __future__ import annotations

import html
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class ReportStep:
    name: str
    status: str
    message: str = ""
    details: dict[str, Any] = field(default_factory=dict)
    started_at: str = field(default_factory=lambda: _now())
    finished_at: str = field(default_factory=lambda: _now())


@dataclass
class ReportArtifact:
    name: str
    path: str
    artifact_type: str = "file"


class TestReport:
    def __init__(self, title: str, output_dir: str | Path = "artifacts/reports"):
        self.title = title
        self.output_dir = Path(output_dir)
        self.steps: list[ReportStep] = []
        self.artifacts: list[ReportArtifact] = []
        self.started_at = _now()
        self.finished_at: str | None = None

    def add_step(
        self,
        name: str,
        status: str,
        message: str = "",
        details: dict[str, Any] | None = None,
    ):
        self.steps.append(
            ReportStep(
                name=name,
                status=status,
                message=message,
                details=details or {},
            )
        )

    def add_artifact(self, name: str, path: str | Path, artifact_type: str = "file"):
        self.artifacts.append(
            ReportArtifact(name=name, path=str(path), artifact_type=artifact_type)
        )

    def write(self, basename: str = "report") -> dict[str, Path]:
        self.finished_at = _now()
        self.output_dir.mkdir(parents=True, exist_ok=True)

        json_path = self.output_dir / f"{basename}.json"
        html_path = self.output_dir / f"{basename}.html"

        json_path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")
        html_path.write_text(self.to_html(), encoding="utf-8")

        return {"json": json_path, "html": html_path}

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "summary": self.summary,
            "steps": [asdict(step) for step in self.steps],
            "artifacts": [asdict(artifact) for artifact in self.artifacts],
        }

    @property
    def summary(self) -> dict[str, int]:
        statuses = {"passed": 0, "failed": 0, "skipped": 0}
        for step in self.steps:
            statuses[step.status] = statuses.get(step.status, 0) + 1
        return statuses

    def to_html(self) -> str:
        step_rows = "\n".join(self._step_row(step) for step in self.steps)
        artifact_rows = "\n".join(self._artifact_row(artifact) for artifact in self.artifacts)
        summary = self.summary

        return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(self.title)}</title>
  <style>
    body {{
      background: #f6f7f9;
      color: #17202a;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      margin: 0;
    }}
    header {{
      background: #18212f;
      color: white;
      padding: 24px 32px;
    }}
    main {{
      max-width: 1120px;
      margin: 0 auto;
      padding: 24px;
    }}
    section {{
      background: white;
      border: 1px solid #d8dee8;
      border-radius: 8px;
      margin-bottom: 20px;
      overflow: hidden;
    }}
    h1, h2 {{
      margin: 0;
    }}
    h2 {{
      font-size: 16px;
      padding: 16px;
      border-bottom: 1px solid #d8dee8;
    }}
    table {{
      border-collapse: collapse;
      width: 100%;
    }}
    th, td {{
      border-bottom: 1px solid #edf0f4;
      font-size: 13px;
      padding: 10px 12px;
      text-align: left;
      vertical-align: top;
    }}
    .summary {{
      display: flex;
      gap: 12px;
      padding: 16px;
    }}
    .metric {{
      border: 1px solid #d8dee8;
      border-radius: 6px;
      padding: 12px;
      min-width: 120px;
    }}
    .passed {{ color: #0b6b3a; font-weight: 700; }}
    .failed {{ color: #a32020; font-weight: 700; }}
    .skipped {{ color: #735c0f; font-weight: 700; }}
    pre {{
      white-space: pre-wrap;
      word-break: break-word;
      margin: 0;
    }}
  </style>
</head>
<body>
  <header>
    <h1>{html.escape(self.title)}</h1>
    <p>Started: {html.escape(self.started_at)} | Finished: {html.escape(self.finished_at or "")}</p>
  </header>
  <main>
    <section>
      <h2>Summary</h2>
      <div class="summary">
        <div class="metric passed">Passed<br>{summary.get("passed", 0)}</div>
        <div class="metric failed">Failed<br>{summary.get("failed", 0)}</div>
        <div class="metric skipped">Skipped<br>{summary.get("skipped", 0)}</div>
      </div>
    </section>
    <section>
      <h2>Steps</h2>
      <table>
        <thead><tr><th>Status</th><th>Name</th><th>Message</th><th>Details</th></tr></thead>
        <tbody>{step_rows}</tbody>
      </table>
    </section>
    <section>
      <h2>Artifacts</h2>
      <table>
        <thead><tr><th>Name</th><th>Type</th><th>Path</th></tr></thead>
        <tbody>{artifact_rows}</tbody>
      </table>
    </section>
  </main>
</body>
</html>
"""

    @staticmethod
    def _step_row(step: ReportStep) -> str:
        details = html.escape(json.dumps(step.details, indent=2))
        return (
            f"<tr><td class='{html.escape(step.status)}'>{html.escape(step.status)}</td>"
            f"<td>{html.escape(step.name)}</td>"
            f"<td>{html.escape(step.message)}</td>"
            f"<td><pre>{details}</pre></td></tr>"
        )

    @staticmethod
    def _artifact_row(artifact: ReportArtifact) -> str:
        return (
            f"<tr><td>{html.escape(artifact.name)}</td>"
            f"<td>{html.escape(artifact.artifact_type)}</td>"
            f"<td>{html.escape(artifact.path)}</td></tr>"
        )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
