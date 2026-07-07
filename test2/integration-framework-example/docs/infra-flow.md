# Infrastructure Flow

This document shows how the infrastructure layer should work when the test
harness, CloudStack VMs, Ansible, and pytest are connected for real.

## Roles

```text
operator or CI
  chooses the desired system config

test harness VM
  owns this repo
  calls CloudStack
  generates Ansible inventory and master config
  runs ansible-playbook
  runs pytest
  stores logs, pcaps, screenshots, and reports

product VMs
  are created from CloudStack templates
  are configured by Ansible
  are tested by pytest from the harness VM
```

The harness VM is not one of the products. It is the controller. Product VMs are
the test targets.

## Big Picture

```text
system config
  -> CloudStack provisioning
  -> generated inventory
  -> generated master config
  -> Ansible configures product templates
  -> pytest reads master config
  -> tests drive product libraries, UI, media, and capture tools
```

## Config Types

There are two important config files.

### 1. Desired System Config

This is written by a human, CI job, or higher-level automation. It says what
system should exist for this test run.

Example: `configs/systems/product1-product2.yaml`

```yaml
environment:
  name: product1-product2-smoke
  network: integration-net
  zone: cloudstack-zone-1
  domain: test.local

harness:
  template: test-harness-template-v4
  service_offering: medium
  tools:
    - pytest
    - ansible
    - tshark
    - gstreamer
    - selenium

products:
  product1:
    enabled: true
    template: product1-template-2026-07-01
    service_offering: large
    ip: 10.50.10.11
    ui_url: https://10.50.10.11
    capabilities:
      - send_udp
      - receive_audio
      - send_audio
      - web_ui
    config:
      media_port: 5000
      api_port: 8443
      mode: sender

  product2:
    enabled: true
    template: product2-template-2026-07-01
    service_offering: medium
    ip: 10.50.10.12
    capabilities:
      - receive_udp
      - receive_audio
    config:
      media_port: 5000
      api_port: 8443
      mode: receiver

  product3:
    enabled: false
    template: product3-template-2026-07-01
    service_offering: medium
    capabilities:
      - send_video
```

This file controls how many products are running. If `enabled: false`, the VM is
not created and pytest should not target it.

### 2. Generated Master Config

This is produced after CloudStack provisioning. It contains the final facts that
Ansible and pytest both need.

Example: `runtime/it-a18f31c2/master-config.json`

```json
{
  "environment_id": "it-a18f31c2",
  "network": {
    "name": "integration-net",
    "cidr": "10.50.10.0/24",
    "domain": "test.local"
  },
  "harness": {
    "name": "harness-it-a18f31c2",
    "ip": "10.50.10.10",
    "template": "test-harness-template-v4"
  },
  "products": {
    "product1": {
      "enabled": true,
      "name": "product1-it-a18f31c2",
      "ip": "10.50.10.11",
      "template": "product1-template-2026-07-01",
      "ui_url": "https://10.50.10.11",
      "capabilities": ["send_udp", "receive_audio", "send_audio", "web_ui"],
      "settings": {
        "media_port": 5000,
        "api_port": 8443,
        "mode": "sender"
      }
    },
    "product2": {
      "enabled": true,
      "name": "product2-it-a18f31c2",
      "ip": "10.50.10.12",
      "template": "product2-template-2026-07-01",
      "ui_url": null,
      "capabilities": ["receive_udp", "receive_audio"],
      "settings": {
        "media_port": 5000,
        "api_port": 8443,
        "mode": "receiver"
      }
    }
  }
}
```

This master config is the contract between infrastructure and tests.

## Generated Ansible Inventory

The same provisioning step should generate an inventory from the master config.

Example: `runtime/it-a18f31c2/inventory.ini`

```ini
[harness]
harness-it-a18f31c2 ansible_host=10.50.10.10 template=test-harness-template-v4

[products]
product1-it-a18f31c2 ansible_host=10.50.10.11 product_key=product1 template=product1-template-2026-07-01
product2-it-a18f31c2 ansible_host=10.50.10.12 product_key=product2 template=product2-template-2026-07-01

[send_udp]
product1-it-a18f31c2

[receive_udp]
product2-it-a18f31c2

[receive_audio]
product1-it-a18f31c2
product2-it-a18f31c2

[web_ui]
product1-it-a18f31c2
```

Capability groups are optional, but they make Ansible targeting easier.

## Ansible Usage

The Ansible playbook should receive the generated master config path.

```bash
ansible-playbook \
  -i runtime/it-a18f31c2/inventory.ini \
  ansible/playbooks/site.yml \
  -e env_id=it-a18f31c2 \
  -e master_config_path=runtime/it-a18f31c2/master-config.json
```

Inside Ansible, load the master config once:

```yaml
- name: Configure integration test products
  hosts: products
  gather_facts: false
  vars_files:
    - "{{ master_config_path }}"
  tasks:
    - name: Pick product config for this host
      ansible.builtin.set_fact:
        product_config: "{{ products[hostvars[inventory_hostname].product_key] }}"

    - name: Render product application config
      ansible.builtin.template:
        src: product.conf.j2
        dest: /etc/product/product.conf
      vars:
        product_ip: "{{ product_config.ip }}"
        media_port: "{{ product_config.settings.media_port }}"
        api_port: "{{ product_config.settings.api_port }}"
        mode: "{{ product_config.settings.mode }}"
```

Template example: `ansible/templates/product.conf.j2`

```ini
environment_id={{ environment_id }}
product_ip={{ product_ip }}
media_port={{ media_port }}
api_port={{ api_port }}
mode={{ mode }}
```

The exact product config files will differ by product, but they should all come
from the same generated master config.

## Pytest Usage

After Ansible configures the VMs, pytest runs from the harness VM:

```bash
python -m pytest \
  --product-config=runtime/it-a18f31c2/master-config.json \
  --product=product1 \
  --suite=suite1
```

Pytest reads the same master config and builds product objects:

```text
master config
  -> ProductRegistry
  -> product1.backend / product1.ui / product1.verify
  -> test suite
```

That means tests do not need to know how the VMs were created. They only need
the final product IPs, URLs, capabilities, and settings.

## Provisioning Sequence

The real implementation can be a Python CLI in this repo:

```bash
python -m framework.infra.provision \
  --system-config configs/systems/product1-product2.yaml \
  --runtime-dir runtime
```

Expected steps:

1. Read desired system config.
2. Create an environment id, for example `it-a18f31c2`.
3. Create or attach the CloudStack network.
4. Create the harness VM if the harness is not already running.
5. Create one product VM for each product with `enabled: true`.
6. Assign requested IPs or record assigned IPs.
7. Wait for SSH/API readiness.
8. Write `runtime/<env_id>/inventory.ini`.
9. Write `runtime/<env_id>/master-config.json`.
10. Run `ansible-playbook` with that inventory and master config.
11. Run pytest from the harness VM.
12. Store artifacts under `runtime/<env_id>/artifacts`.
13. Destroy VMs unless the run uses a keep flag.

## What CloudStack Needs From Config

Each VM needs enough data to call CloudStack APIs:

```yaml
template: product1-template-2026-07-01
service_offering: large
network: integration-net
ip: 10.50.10.11
display_name: product1-it-a18f31c2
ssh_keypair: integration-test-key
security_groups:
  - integration-products
```

The desired config can omit IPs if CloudStack should assign them dynamically.
If IPs are dynamic, the generated master config must record the final assigned
addresses before Ansible and pytest run.

## Harness VM Contents

The harness template should include:

```text
python
pytest
ansible
cloudstack client or API credentials
ssh private key for product VMs
tshark or tcpdump
gstreamer
browser plus browser driver if UI tests run from harness
this repo or a checkout step
artifact storage path
```

The harness also needs network access to every product VM on the ports required
for SSH, API, UI, media, and packet capture.

## Product VM Contents

Product templates should be close to production images, but with test hooks
enabled where needed:

```text
product software installed or installable by Ansible
SSH access for Ansible
config directory writable by Ansible
logs readable by test automation
optional test-mode TLS key logging or protocol event logging
media ports open
API/UI ports open
```

## Why This Scales

The number of active products is controlled by the desired system config.
CloudStack only creates enabled products. Ansible only configures inventory
hosts that exist. Pytest only builds product objects from the generated master
config.

So a two-product run and a 35-product run use the same flow:

```text
different desired config
same provisioner
same Ansible playbooks
same pytest harness
different generated master config
```

## Failure Points To Design For

The provisioner should fail early if:

- a requested template does not exist;
- a requested static IP is already taken;
- a product is enabled without required capabilities;
- Ansible cannot reach a VM over SSH;
- the generated master config does not match the inventory;
- pytest asks for a product that is not in the master config.

The master config should be saved even on failure so the run can be debugged.
