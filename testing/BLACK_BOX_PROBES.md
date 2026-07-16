# Black-Box Probes

This framework can run from a test VM and act as an external peer to the product under test.

For an audio product, that means the VM can:

- Call the product backend API.
- Send audio into the product.
- Receive audio from the product.
- Capture packets on the network interface.
- Produce JSON and HTML reports for pytest runs.

The design adds a `probes` layer:

```text
Product
  api
  ui optional
  probes optional
    gstreamer
    wireshark/tshark
  report
```

## Probe Config

Example: [configs/audio_device_product.yml](/Users/kayleekhang/kyle-june-26/test-framework/testing/configs/audio_device_product.yml:1)

```yaml
probes:
  send_test_tone:
    type: gstreamer
    timeout_seconds: 10
    pipeline: audiotestsrc wave=sine freq=1000 num-buffers=500 ! audioconvert ! audioresample ! mulawenc ! rtppcmupay ! udpsink host=127.0.0.1 port=5004

  audio_packets:
    type: wireshark
    interface: lo0
    capture_filter: udp port 5004
    output_path: artifacts/captures/audio_packets.pcapng
    timeout_seconds: 10
```

Use `lo0` for local macOS loopback, `lo` for Linux loopback, or a real VM interface such as `eth0`, `ens160`, or `enp0s3`.

## Python Usage

```python
from config import load_product_config
from products import ProductFactory
from reporting import TestReport


def test_audio_packets_are_emitted():
    config = load_product_config("configs/audio_device_product.yml")
    product = ProductFactory.create(driver=None, config=config)
    report = TestReport("audio packet test")

    response = product.api.request("health")
    report.add_step(
        "health endpoint",
        "passed" if response.ok else "failed",
        details={"status_code": response.status_code, "error": response.error},
    )

    capture = product.capture_audio_packets(timeout_seconds=5)
    report.add_step(
        "capture audio packets",
        "passed" if capture.ok else "failed",
        details={"stderr": capture.stderr, "error": capture.error},
    )

    for artifact in capture.artifacts:
        report.add_artifact("packet capture", artifact, "pcapng")

    paths = report.write("audio-packet-test")

    assert response.ok
    assert capture.ok
```

## GStreamer CLI

Run an inline pipeline:

```bash
python cli.py gst-run \
  --timeout 10 \
  --pipeline 'audiotestsrc wave=sine freq=1000 num-buffers=500 ! audioconvert ! audioresample ! fakesink'
```

Run a configured GStreamer probe:

```bash
python cli.py gst-probe \
  --config configs/audio_device_product.yml \
  --probe send_test_tone \
  --timeout 10
```

## Wireshark/tshark CLI

Capture packets directly:

```bash
python cli.py tshark-capture \
  --interface eth0 \
  --capture-filter 'udp port 5004' \
  --output artifacts/captures/audio_packets.pcapng \
  --timeout 10
```

Run a configured packet capture probe:

```bash
python cli.py tshark-probe \
  --config configs/audio_device_product.yml \
  --probe audio_packets \
  --timeout 10
```

## Reports

Create a demo report:

```bash
python cli.py report-demo --output-dir artifacts/reports
```

In pytest, create one report per test or per scenario. The report object writes:

- `report.json` for machines and CI.
- `report.html` for humans.

This is intentionally not a Robot Framework clone, but it keeps the useful parts:

- Step-by-step output
- Pass/fail status
- Details and errors
- Linked artifacts such as `.pcapng`, logs, and screenshots
- HTML plus JSON output

## Scaling Rule

Use probes for observation mechanisms:

- HTTP belongs in `API`.
- Selenium belongs in `Page` and `UiElement`.
- GStreamer belongs in `GStreamerProbe`.
- tshark belongs in `WiresharkProbe`.
- Logs/files/serial can become future probes.

Use product subclasses for domain behavior. The sample audio config uses `product_type: audio_device`, which creates `AudioDeviceProduct`:

```python
class AudioDeviceProduct(Product):
    def send_test_tone(self):
        return self.probe("send_test_tone").run_pipeline()

    def capture_audio_packets(self):
        return self.probe("audio_packets").capture()
```

That keeps tool mechanics separate from product meaning.
