# Ansible Deployment

Use Ansible to install this test framework onto test VMs, Raspberry Pis, or WIC-like hardware targets.

The target machine becomes the black-box test node:

```text
test node
  runs pytest
  calls product backend APIs
  drives Selenium if browser/UI testing is needed
  runs gst-launch-1.0 for audio/media probes
  runs tshark for packet captures
  writes reports and artifacts
```

## Files

Example files:

- [ansible/inventory.example.ini](/Users/kayleekhang/kyle-june-26/test-framework/testing/ansible/inventory.example.ini:1)
- [ansible/deploy_test_framework.yml](/Users/kayleekhang/kyle-june-26/test-framework/testing/ansible/deploy_test_framework.yml:1)

## Run Deployment

From `test-framework/testing`:

```bash
ansible-playbook \
  -i ansible/inventory.example.ini \
  ansible/deploy_test_framework.yml
```

Override install location:

```bash
ansible-playbook \
  -i ansible/inventory.example.ini \
  ansible/deploy_test_framework.yml \
  -e test_framework_dest=/opt/my-test-framework
```

Skip media tools for backend-only nodes:

```bash
ansible-playbook \
  -i ansible/inventory.example.ini \
  ansible/deploy_test_framework.yml \
  -e install_gstreamer=false \
  -e install_tshark=false
```

## Target Types

Use inventory groups to distinguish target classes:

```ini
[test_vms]
test-vm-1 ansible_host=192.168.56.20 ansible_user=ubuntu test_framework_profile=vm

[raspberry_pis]
pi-audio-1 ansible_host=192.168.56.30 ansible_user=pi test_framework_profile=pi

[wics]
wic-1 ansible_host=192.168.56.40 ansible_user=ubuntu test_framework_profile=wic
```

The same framework can run everywhere, but host vars should describe hardware differences:

- network interface, such as `eth0`, `ens160`, `wlan0`, or `lo`
- whether GStreamer is installed
- whether tshark is installed
- product IPs and ports
- audio device names
- browser availability for Selenium

## Recommended Host Vars

Example:

```yaml
test_framework_profile: pi
capture_interface: eth0
audio_input_device: hw:1,0
audio_output_device: hw:1,0
product_api_host: 192.168.56.100
product_api_port: 8080
```

Use those values to generate product test YAML before running pytest.

## Operational Config Flow

Recommended flow:

```text
1. Ansible provisions the test node.
2. Ansible installs Python dependencies and external tools.
3. Ansible writes or templates generated product test configs.
4. pytest runs on the test node.
5. Reports and artifacts are collected from artifacts/.
```

You can template configs with Ansible:

```text
templates/audio_device_product.yml.j2
  -> /opt/blackbox-testing/configs/audio_device_product.yml
```

The template can fill operational values:

```yaml
host: "{{ product_api_host }}"
port: {{ product_api_port }}
interface: "{{ capture_interface }}"
```

Keep test-only values in the template or test config:

- `test_tag`
- probe names
- packet filters
- expected status names
- timeouts

## Running Tests Remotely

After deployment:

```bash
ssh ubuntu@test-vm-1
cd /opt/blackbox-testing
source .venv/bin/activate
pytest
```

Run a CLI probe:

```bash
python cli.py tshark-probe \
  --config configs/audio_device_product.yml \
  --probe audio_packets \
  --timeout 10
```

Run a GStreamer probe:

```bash
python cli.py gst-probe \
  --config configs/audio_device_product.yml \
  --probe send_test_tone \
  --timeout 10
```

## Collect Artifacts

Reports and captures live under:

```text
artifacts/
  captures/
  reports/
```

Collect them with Ansible:

```yaml
- name: Fetch artifacts
  ansible.builtin.fetch:
    src: /opt/blackbox-testing/artifacts/
    dest: ./artifacts/{{ inventory_hostname }}/
    flat: false
```

## Notes for Raspberry Pis

Raspberry Pis may need extra setup:

- install OS packages for audio drivers
- configure ALSA/PulseAudio/PipeWire depending on your image
- ensure the test user can access audio devices
- ensure the test user can run packet captures

For tshark packet capture, you may need to configure dumpcap permissions or run the test process with elevated privileges.

## Notes for WICs

Treat WICs like constrained test nodes:

- keep dependencies explicit
- avoid assuming a browser is installed
- use backend and probe tests when UI is unavailable
- use Ansible host vars for interface/device differences
- collect logs and captures aggressively because interactive debugging is harder

