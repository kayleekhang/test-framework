from __future__ import annotations

import argparse
import sys
from pathlib import Path

from config import load_product_config
from products import ProductFactory
from probes import GStreamerProbe, WiresharkProbe
from reporting import TestReport


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Black-box product testing helpers")
    subcommands = parser.add_subparsers(dest="command", required=True)

    gst_run = subcommands.add_parser("gst-run", help="Run a GStreamer pipeline")
    gst_run.add_argument("--pipeline", required=True)
    gst_run.add_argument("--timeout", type=int, default=10)

    gst_probe = subcommands.add_parser("gst-probe", help="Run a configured GStreamer probe")
    gst_probe.add_argument("--config", required=True)
    gst_probe.add_argument("--probe", required=True)
    gst_probe.add_argument("--timeout", type=int)

    tshark_capture = subcommands.add_parser("tshark-capture", help="Capture packets with tshark")
    tshark_capture.add_argument("--interface", required=True)
    tshark_capture.add_argument("--capture-filter")
    tshark_capture.add_argument("--output", required=True)
    tshark_capture.add_argument("--timeout", type=int, default=10)

    tshark_probe = subcommands.add_parser("tshark-probe", help="Run a configured tshark probe")
    tshark_probe.add_argument("--config", required=True)
    tshark_probe.add_argument("--probe", required=True)
    tshark_probe.add_argument("--timeout", type=int)

    report_demo = subcommands.add_parser("report-demo", help="Create an example HTML/JSON report")
    report_demo.add_argument("--output-dir", default="artifacts/reports")

    args = parser.parse_args(argv)

    if args.command == "gst-run":
        probe = GStreamerProbe(
            name="cli_gstreamer",
            config={"type": "gstreamer", "pipeline": args.pipeline, "timeout_seconds": args.timeout},
        )
        result = probe.run_pipeline(args.timeout)
        return _print_result(result)

    if args.command == "gst-probe":
        product = _load_product(args.config)
        result = product.probe(args.probe).run_pipeline(args.timeout)
        return _print_result(result)

    if args.command == "tshark-capture":
        probe = WiresharkProbe(
            name="cli_tshark",
            config={
                "type": "wireshark",
                "interface": args.interface,
                "capture_filter": args.capture_filter,
                "output_path": args.output,
                "timeout_seconds": args.timeout,
            },
        )
        result = probe.capture(args.timeout)
        return _print_result(result)

    if args.command == "tshark-probe":
        product = _load_product(args.config)
        result = product.probe(args.probe).capture(args.timeout)
        return _print_result(result)

    if args.command == "report-demo":
        report = TestReport("Demo Black-Box Test Report", args.output_dir)
        report.add_step("health endpoint", "passed", "HTTP 200")
        report.add_step("audio stream", "failed", "No RTP packets observed", {"packet_count": 0})
        paths = report.write("demo-report")
        print(f"JSON: {paths['json']}")
        print(f"HTML: {paths['html']}")
        return 0

    return 1


def _load_product(config_path: str):
    config = load_product_config(Path(config_path))
    return ProductFactory.create(driver=None, config=config)


def _print_result(result) -> int:
    print(f"name={result.name}")
    print(f"type={result.probe_type}")
    print(f"ok={result.ok}")
    print(f"return_code={result.return_code}")
    print(f"command={' '.join(result.command)}")
    if result.artifacts:
        print(f"artifacts={','.join(result.artifacts)}")
    if result.stdout:
        print("stdout:")
        print(result.stdout)
    if result.stderr:
        print("stderr:")
        print(result.stderr)
    if result.error:
        print(f"error={result.error}")
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
