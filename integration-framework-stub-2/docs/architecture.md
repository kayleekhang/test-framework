# Architecture

The framework models embedded integration testing as layers:

```text
pytest test
  ↓
System
  ↓
Product
  ↓
Application
  ↓
Target / launch mode
```

## Layer Responsibilities

| Layer | Owns | Example |
|---|---|---|
| Test | Scenario and assertions | `test_vehicle_system_boots` |
| System | Product composition | `VehicleSystem` |
| Product | Product-specific behavior | `GpsProduct.publish_position()` |
| Application | Start/stop/build/log collection | `SystemdApplication` |
| Target | Where it runs | `vm`, `amd64`, `arm64` |

## Why this scales

New systems reuse existing products.

New products reuse existing application modes.

New applications are usually just YAML entries.

New test types are pytest markers and folders.

New hardware/start modes are new `Application` classes.
