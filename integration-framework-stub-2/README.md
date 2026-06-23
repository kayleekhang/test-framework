# Embedded Integration Framework Stub

This repo is a **stubbed Python integration-test framework** for embedded-style systems.

It is meant to model this real-world idea:

```text
A system is made of products.
A product is made of one or more applications.
An application runs on a target.
A test starts a system and verifies behavior across products.
```

Example:

```text
Vehicle System
├── GPS Product
│   └── gps-sim application
├── Radio Product
│   ├── radio-service application
│   └── radio-health application
└── Controller Product
    ├── controller-main application
    └── controller-watchdog application
```

The framework is designed so test code does **not** need to know whether a product is:

- real hardware
- a simulator
- a local binary
- a remote binary over SSH
- a systemd service
- built for `vm`, `amd64`, or `arm64`

That decision comes from config.

---

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

pytest -q
```

Run by test type:

```bash
pytest -m smoke
pytest -m integration
pytest -m system
pytest -m security
```

Build the same system for different targets:

```bash
python tools/build_system.py --config configs/systems/vehicle_system.yaml --target vm
python tools/build_system.py --config configs/systems/vehicle_system.yaml --target amd64
python tools/build_system.py --config configs/systems/vehicle_system.yaml --target arm64
```

---

# The Big Picture

The architecture flows like this:

```text
pytest test
   ↓
pytest fixture
   ↓
ConfigLoader
   ↓
SystemFactory
   ↓
VehicleSystem
   ↓
ProductFactory
   ↓
GPS / Radio / Controller products
   ↓
ApplicationFactory
   ↓
local binary / remote binary / systemd / simulator application
```

The most important design rule is:

> Tests talk to systems.  
> Systems own products.  
> Products own applications.  
> Applications know how to start, stop, build, and collect logs.

That keeps tests clean and keeps product-specific complexity out of the test files.

---

# Project Layout

```text
integration-framework-stub/
│
├── framework/
│   ├── applications/
│   │   ├── base_application.py
│   │   ├── local_binary_application.py
│   │   ├── remote_binary_application.py
│   │   ├── simulator_application.py
│   │   └── systemd_application.py
│   │
│   ├── products/
│   │   ├── base_product.py
│   │   ├── gps/gps_product.py
│   │   ├── radio/radio_product.py
│   │   └── controller/controller_product.py
│   │
│   ├── systems/
│   │   ├── base_system.py
│   │   └── vehicle_system.py
│   │
│   ├── factory/
│   │   ├── application_factory.py
│   │   ├── product_factory.py
│   │   ├── system_factory.py
│   │   └── config_loader.py
│   │
│   └── common/
│       ├── exceptions.py
│       └── models.py
│
├── configs/
│   ├── systems/
│   │   └── vehicle_system.yaml
│   ├── targets/
│   │   ├── vm.yaml
│   │   ├── amd64.yaml
│   │   └── arm64.yaml
│   └── test_suites/
│       └── smoke.yaml
│
├── tests/
│   ├── smoke/
│   ├── integration/
│   ├── system/
│   └── security/
│
├── tools/
│   ├── build_system.py
│   └── run_system.py
│
└── docs/
    └── architecture.md
```

---

# Core Concepts

## 1. System

A **system** is the thing you are testing as a whole.

Examples:

```text
VehicleSystem
SecuritySystem
CommunicationsSystem
GroundStationSystem
RadarSystem
```

A system knows which products belong together.

In this repo:

```python
framework/systems/vehicle_system.py
```

creates:

```text
gps
radio
controller
```

The system exposes high-level behavior:

```python
vehicle_system.startup()
vehicle_system.shutdown()
vehicle_system.nominal_mission_flow()
vehicle_system.collect_artifacts()
```

Your tests should mostly call methods on the system.

---

## 2. Product

A **product** is a deployable unit inside the system.

Examples:

```text
GPS product
Radio product
Controller product
Camera product
Display product
TPM product
Gateway product
```

A product may contain one or more applications.

Example:

```text
Radio Product
├── radio-service
└── radio-health
```

In this repo:

```text
framework/products/gps/gps_product.py
framework/products/radio/radio_product.py
framework/products/controller/controller_product.py
```

Each product inherits from:

```text
framework/products/base_product.py
```

The base product already knows how to:

```python
build()
start()
stop()
health_check()
collect_logs()
wait_for_state()
```

Specific products add product-specific actions:

```python
gps.publish_position(...)
radio.transmit(...)
controller.command(...)
```

---

## 3. Application

An **application** is an actual binary/service/process that belongs to a product.

Examples:

```text
controller-main
controller-watchdog
radio-service
radio-health
gps-sim
```

An application knows how it is launched.

Current launch modes:

```text
local_binary
remote_binary
systemd
simulator
```

These map to:

```text
framework/applications/local_binary_application.py
framework/applications/remote_binary_application.py
framework/applications/systemd_application.py
framework/applications/simulator_application.py
```

This lets one product have multiple binaries while still looking like one product to the system.

---

## 4. Target

A **target** is where the application is built or expected to run.

Current stub targets:

```text
vm
amd64
arm64
```

Examples:

```yaml
target: arm64
```

or:

```bash
python tools/build_system.py --config configs/systems/vehicle_system.yaml --target arm64
```

Right now the build is stubbed. It creates fake build artifacts.

Later, this is where you would connect:

```text
CMake
Make
Cargo
Bazel
Docker build
Yocto
cross-compilers
scp deploy
systemd install
```

---

## 5. Test Type

Tests are grouped by folder and pytest marker.

```text
tests/smoke/          quick boot/health tests
tests/integration/    product-to-product behavior
tests/system/         full system behavior
tests/security/       crypto/auth/failure security behavior
tests/performance/    load/timing tests
tests/soak/           long duration tests
```

Markers are registered in:

```text
pytest.ini
```

Run them like:

```bash
pytest -m smoke
pytest -m "integration or security"
pytest -m "not soak"
```

---

# How the YAML Config Works

The main config is:

```text
configs/systems/vehicle_system.yaml
```

It defines:

```yaml
system_name: vehicle-demo
system_type: vehicle
target: vm

products:
  gps:
    product_type: gps
    mode: simulator
    target: vm
    applications:
      - name: gps-sim
        binary_name: gps_sim
        args: ["--rate", "10"]
    settings:
      update_rate_hz: 10
      protocol: nmea

  radio:
    product_type: radio
    mode: local_binary
    target: amd64
    applications:
      - name: radio-service
        binary_name: radio_service
        args: ["--frequency", "915"]
      - name: radio-health
        binary_name: radio_health
        args: []
    settings:
      frequency_mhz: 915
      power_dbm: 20

  controller:
    product_type: controller
    mode: systemd
    target: arm64
    applications:
      - name: controller-main
        binary_name: controller_main
        args: ["--profile", "integration"]
      - name: controller-watchdog
        binary_name: controller_watchdog
        args: []
    settings:
      host: 192.168.1.30
      ssh_user: test
      service_name: controller.service
```

This is what makes the framework modular.

The code does not hardcode every binary.  
The YAML declares which products and applications exist.

---

# How It Scales

## Scaling to a New System

Suppose you want to add:

```text
SecuritySystem
├── Camera Product
├── Radar Product
├── Radio Product
└── Display Product
```

You add:

```text
framework/systems/security_system.py
configs/systems/security_system.yaml
```

Then register it in:

```text
framework/factory/system_factory.py
```

Example:

```python
if config.system_type == "security":
    return SecuritySystem(config)
```

Now tests can load that system.

Example test:

```python
@pytest.mark.smoke
def test_security_system_boots(security_system):
    security_system.startup()
    assert security_system.wait_until_healthy()
```

The new system can reuse existing products like `radio`, while adding new ones like `camera` and `radar`.

---

## Scaling to a New Product

Suppose you add a camera product.

Add:

```text
framework/products/camera/
├── __init__.py
└── camera_product.py
```

Example:

```python
from framework.products.base_product import BaseProduct

class CameraProduct(BaseProduct):
    def inject_frame(self, frame_name: str):
        print(f"[CAMERA] inject frame: {frame_name}")
```

Then update:

```text
framework/factory/product_factory.py
```

```python
from framework.products.camera.camera_product import CameraProduct

if config.product_type == "camera":
    return CameraProduct(config)
```

Then use it in YAML:

```yaml
camera:
  product_type: camera
  mode: simulator
  target: vm
  applications:
    - name: camera-sim
      binary_name: camera_sim
      args: ["--fps", "30"]
  settings:
    resolution: 1080p
    fps: 30
```

Now any system can use the camera product.

---

## Scaling to a New Application Inside a Product

Suppose the controller now has three binaries:

```text
controller-main
controller-watchdog
controller-diagnostics
```

You do not need a new product type.

Just add one more application in YAML:

```yaml
controller:
  product_type: controller
  mode: systemd
  target: arm64
  applications:
    - name: controller-main
      binary_name: controller_main
      args: ["--profile", "integration"]
    - name: controller-watchdog
      binary_name: controller_watchdog
      args: []
    - name: controller-diagnostics
      binary_name: controller_diag
      args: ["--port", "8080"]
  settings:
    host: 192.168.1.30
    ssh_user: test
    service_name: controller.service
```

The base product starts each application automatically.

---

## Scaling to a New Simulator

There are two approaches.

### Simple Simulator

If the simulator behaves like a normal application, just use:

```yaml
mode: simulator
```

Example:

```yaml
gps:
  product_type: gps
  mode: simulator
  applications:
    - name: gps-sim
      binary_name: gps_sim
      args: ["--rate", "10"]
```

### Custom Simulator

If the simulator needs special behavior, create a product method.

Example:

```python
class GpsProduct(BaseProduct):
    def publish_position(self, lat: float, lon: float):
        print(f"[GPS] publish position lat={lat}, lon={lon}")
```

Now tests can do:

```python
vehicle_system.gps.publish_position(28.0, -82.0)
```

Later this could send a UDP packet, write serial data, publish NATS messages, or replay a PCAP.

---

## Scaling to a New Application Start Mode

Current start modes are:

```text
local_binary
remote_binary
systemd
simulator
```

Suppose you want:

```text
docker
```

Add:

```text
framework/applications/docker_application.py
```

Example:

```python
class DockerApplication(BaseApplication):
    def start(self):
        print(f"docker run {self.config.binary_name}")
        self.running = True

    def stop(self):
        print(f"docker stop {self.config.binary_name}")
        self.running = False
```

Then register it in:

```text
framework/factory/application_factory.py
```

```python
if mode == "docker":
    return DockerApplication(product_name, app_config, product_settings)
```

Then YAML can use:

```yaml
mode: docker
```

No tests need to change.

---

## Scaling to New Test Types

Add a folder:

```text
tests/fault_injection/
```

Add a marker in:

```text
pytest.ini
```

```ini
markers =
    fault_injection: cable pulls, process kills, power loss, packet corruption
```

Then write tests:

```python
import pytest

@pytest.mark.fault_injection
def test_controller_recovers_after_gps_loss(vehicle_system):
    vehicle_system.startup()

    vehicle_system.gps.stop()
    assert vehicle_system.controller.wait_for_state("DEGRADED")
```

Run:

```bash
pytest -m fault_injection
```

---

# Why This Is Modular

The modularity comes from the layers:

```text
Test
  depends on System

System
  depends on Products

Product
  depends on Applications

Application
  depends on launch/build strategy
```

So when something changes, the impact stays local.

## Example: Add a product

You change:

```text
framework/products/new_product/
framework/factory/product_factory.py
configs/systems/*.yaml
```

You usually do **not** change:

```text
existing tests
existing applications
existing systems that do not use the product
```

## Example: Add a system

You change:

```text
framework/systems/new_system.py
framework/factory/system_factory.py
configs/systems/new_system.yaml
tests/new_system/
```

You usually do **not** change:

```text
existing products
existing application launch code
```

## Example: Change a binary name

You change only YAML:

```yaml
binary_name: new_controller_main
```

You do **not** change test code.

## Example: Switch from simulator to real hardware

Change YAML:

```yaml
mode: simulator
```

to:

```yaml
mode: remote_binary
settings:
  host: 192.168.1.50
  ssh_user: test
```

Tests stay the same.

---

# Example Test Flow

A smoke test:

```python
@pytest.mark.smoke
def test_vehicle_system_boots(vehicle_system):
    vehicle_system.startup()

    assert vehicle_system.gps.health_check()
    assert vehicle_system.radio.health_check()
    assert vehicle_system.controller.wait_for_state("READY")
```

This test does not know:

- how many binaries each product has
- whether GPS is real or simulated
- whether controller is ARM64
- whether radio runs locally
- how logs are collected

That is intentional.

---

# What This Stub Does Not Do Yet

This repo is intentionally a starting point.

It does not yet do real:

```text
SSH
serial console
power control
packet capture
cross-compilation
scp deployment
systemd installation
Docker orchestration
hardware flashing
log parsing
JUnit/Allure reporting
```

But the structure gives you places to add those features without rewriting the whole framework.

Suggested future folders:

```text
framework/infrastructure/ssh/
framework/infrastructure/serial/
framework/infrastructure/power/
framework/infrastructure/network/
framework/infrastructure/packet_capture/
framework/reporting/
framework/deployment/
```

---

# Recommended Growth Path

Start simple:

```text
1. One system
2. Three products
3. One simulator
4. Smoke tests
```

Then add:

```text
5. Integration tests
6. Real hardware mode
7. Remote SSH start/stop
8. Log collection
9. Fault injection
10. Build/deploy pipeline
```

Do not start with every feature.  
The framework scales because each concept has a place.

---

# Summary

Use this framework like this:

```text
Add a system when you have a new combination of products.

Add a product when you have a new device/service type.

Add an application when a product has another binary/process.

Add a start mode when applications need a new way to run.

Add a test type when you need a new category of validation.

Change YAML when the system composition changes.
```

The goal is to keep tests readable:

```python
vehicle_system.startup()
vehicle_system.nominal_mission_flow()
assert vehicle_system.wait_until_healthy()
```

while hiding the messy details of binaries, targets, simulators, hardware, and deployment behind the framework.
