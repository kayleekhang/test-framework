# Black-Box Probes

Probes are composed into products through `ProductBuilder`.

Supported adapters currently include:

- GStreamer pipelines
- Wireshark/tshark packet capture

## Defining probes

```python
from builders import ProductBuilder

builder = (
    ProductBuilder("audio_device")
    .with_probe(
        "send_test_tone",
        type="gstreamer",
        timeout_seconds=10,
        pipeline=(
            "audiotestsrc wave=sine freq=1000 num-buffers=500 ! "
            "audioconvert ! audioresample ! fakesink"
        ),
    )
    .with_probe(
        "audio_packets",
        type="wireshark",
        interface="lo0",
        capture_filter="udp port 5004",
        output_path="artifacts/captures/audio_packets.pcapng",
        timeout_seconds=10,
    )
)
```

The standard audio definition is available from:

```python
from products import audio_device_product_builder
```

## Running a probe

```python
product = audio_device_product_builder().build(
    name="audio-1",
    ip="10.0.0.20",
)

tone = product.probe("send_test_tone").run_pipeline()
capture = product.probe("audio_packets").capture()

assert tone.ok
assert capture.ok
```

## CLI

The existing CLI commands remain available:

```bash
python cli.py gst-run \
  --pipeline "audiotestsrc num-buffers=100 ! fakesink" \
  --timeout 10
```

```bash
python cli.py gst-probe \
  --config configs/audio_device_product.yml \
  --probe send_test_tone
```

```bash
python cli.py tshark-capture \
  --interface lo0 \
  --capture-filter "udp port 5004" \
  --output artifacts/captures/audio.pcapng
```

The legacy audio YAML is currently used by CLI command selection; reusable probe
definitions used by pytest live in `audio_device_product_builder()`.

## Operational scaling

One builder can create several probe-capable products:

```python
products = audio_device_product_builder().build_many([
    {"name": "audio-1", "ip": "10.0.0.20"},
    {"name": "audio-2", "ip": "10.0.0.21"},
])
```

Probe configuration is copied for each product. Runtime results and artifacts
remain independent.

## Platform notes

- macOS loopback is usually `lo0`.
- Linux loopback is usually `lo`.
- Remote devices commonly use interfaces such as `eth0`, `ens160`, or `enp0s3`.
- GStreamer, tshark, and required OS permissions must exist on the machine that
  executes the probes.
