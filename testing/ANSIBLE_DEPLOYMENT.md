# Ansible Deployment

Ansible installs the test runtime and deploys operational configuration.
Reusable product capabilities remain Python code in the test package.

## What to deploy

```text
testing/
  api.py
  builders.py
  factory.py
  products.py
  probes.py
  websockets_client.py
  conftest.py
  requirements.txt
  configs/
    operational_config.yml
  ui/
  tests/
```

`display_product.yml` no longer exists. Display pages and capabilities are
defined by `display_product_builder()` in `products.py`.

## Operational inventory

Ansible may render or copy a site-specific operational file:

```yaml
productTypeOne:
  builder: display
  instances:
    - name: p1
      ip: 10.20.0.11
    - name: p2
      ip: 10.20.0.12

audioDevices:
  builder: audio_device
  instances:
    - name: audio-1
      ip: 10.20.0.30
```

Names and addresses may be derived from Ansible inventory variables. Builder
names must match those registered by the pytest fixture or application entry
point.

## Example variables

```yaml
test_framework_root: /opt/product-testing
test_operational_config: /etc/product-testing/site.yml
test_python: /opt/product-testing/.venv/bin/python
```

## Installation

Install Python dependencies:

```yaml
- name: Install Python requirements
  ansible.builtin.pip:
    requirements: "{{ test_framework_root }}/requirements.txt"
    virtualenv: "{{ test_framework_root }}/.venv"
```

Install external probe tools only on hosts that execute those probes:

```yaml
- name: Install probe packages
  ansible.builtin.package:
    name:
      - gstreamer1.0-tools
      - tshark
    state: present
```

Browser packages are required only for UI tests. The Selenium wrapper creates
the configured driver lazily.

## Running remotely

```yaml
- name: Run black-box tests
  ansible.builtin.command:
    argv:
      - "{{ test_framework_root }}/.venv/bin/pytest"
      - "{{ test_framework_root }}/tests"
      - "--operational-config"
      - "{{ test_operational_config }}"
  args:
    chdir: "{{ test_framework_root }}"
```

Filter qualification runs as needed:

```yaml
- name: Run display requirement
  ansible.builtin.command:
    argv:
      - "{{ test_framework_root }}/.venv/bin/pytest"
      - "--operational-config"
      - "{{ test_operational_config }}"
      - "--product"
      - "display"
      - "--requirement"
      - "REQ-101"
```

## Artifacts

Create a writable artifact directory:

```yaml
- name: Create artifact directory
  ansible.builtin.file:
    path: "{{ test_framework_root }}/artifacts"
    state: directory
    mode: "0755"
```

Collect it after the test:

```yaml
- name: Fetch test artifacts
  ansible.builtin.fetch:
    src: "{{ test_framework_root }}/artifacts/"
    dest: "./collected-artifacts/"
    flat: false
```

## Deployment rules

- Operations and inventory determine names and addresses.
- Python builders determine capabilities, pages, elements, probes, and ports.
- Use operational overrides for site-specific UI protocols and ports.
- Do not generate capability YAML.
- Ensure each instance name is unique within its operational group because the
  name is appended to UI test tags.
