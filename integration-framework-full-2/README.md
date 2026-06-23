# Integration Framework Full

A working, stubbed integration-test framework for embedded/system-of-systems testing.

It models this lifecycle:

```text
System
  ↓
Products
  ↓
Applications
  ↓
Builder
  ↓
Deployer
  ↓
Launcher
  ↓
Tests
```

## What works now

This repo includes real Python framework code for:

- Loading YAML system configs
- Creating systems with `SystemFactory`
- Creating products with `ProductFactory`
- Creating applications with `ApplicationFactory`
- Building application artifacts with builder stubs
- Deploying artifacts with deployer stubs
- Launching and stopping apps with launcher stubs
- Collecting logs/artifacts
- Running pytest smoke, integration, system, security, performance, soak, and fault-injection tests

The builders/deployers/launchers are **safe stubs**. They print and write artifacts instead of touching real hardware.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

pytest -q
```

## Common commands

Build system:

```bash
python tools/build_system.py --config configs/systems/vehicle_system.yaml --target vm
```

Deploy system:

```bash
python tools/deploy_system.py --config configs/systems/vehicle_system.yaml --target vm
```

Launch system:

```bash
python tools/launch_system.py --config configs/systems/vehicle_system.yaml --target vm
```

Stop system:

```bash
python tools/stop_system.py --config configs/systems/vehicle_system.yaml --target vm
```

Run test categories:

```bash
pytest -m smoke
pytest -m integration
pytest -m system
pytest -m security
pytest -m fault_injection
```

## Architecture

```text
pytest
  ↓
Fixture
  ↓
ConfigLoader
  ↓
SystemFactory
  ↓
VehicleSystem / SecuritySystem
  ↓
ProductFactory
  ↓
GpsProduct / RadioProduct / ControllerProduct / CameraProduct / TpmProduct
  ↓
ApplicationFactory
  ↓
Application
  ↓
Builder + Deployer + Launcher
```

## How it scales

### Add a new system

1. Add a system class under `framework/systems/<name>/`.
2. Register it in `framework/factory/system_factory.py`.
3. Add YAML under `configs/systems/<name>_system.yaml`.
4. Add tests under `tests/`.

### Add a new product

1. Add product class under `framework/products/<name>/`.
2. Register it in `framework/factory/product_factory.py`.
3. Use it in a system YAML config.

### Add a new application

Usually no code change is needed. Add another application to YAML:

```yaml
applications:
  - name: controller-main
    binary_name: controller_main
  - name: controller-watchdog
    binary_name: controller_watchdog
```

### Add a new builder

1. Add class under `framework/build/<tool>/`.
2. Register it in `framework/factory/builder_factory.py`.
3. Use it in YAML with `builder: <name>`.

### Add a new deployer

1. Add class under `framework/deploy/<tool>/`.
2. Register it in `framework/factory/deployer_factory.py`.
3. Use it in YAML with `deployer: <name>`.

### Add a new launcher

1. Add class under `framework/launch/<tool>/`.
2. Register it in `framework/factory/launcher_factory.py`.
3. Use it in YAML with `launcher: <name>`.

### Add a new test type

1. Add a folder under `tests/`.
2. Add marker to `pytest.ini`.
3. Run with `pytest -m <marker>`.

## Important idea

The tests should not care if a product is real hardware, simulator, Docker, systemd, ARM64, AMD64, or VM.

Tests talk to systems:

```python
vehicle_system.startup()
vehicle_system.nominal_mission_flow()
assert vehicle_system.wait_until_healthy()
```

The YAML decides how things are built, deployed, and launched.
