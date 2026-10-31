# Xiaomi Smart Air Purifier 4 Compact — Home Assistant Custom Integration

100% local Home Assistant integration for the **Xiaomi Smart Air Purifier 4 Compact (`xiaomi.airp.cpa4`)**, over the miIO/MIoT protocol (python-miio). No cloud after setup.

Built on the pattern of `ha-xiaomi-feeder-2`; property map from the MIoT spec:
https://miot-spec.org/miot-spec-v2/instance?type=urn:miot-spec-v2:device:air-purifier:0000A007:xiaomi-cpa4:2

## Entities

| Entity | MIoT | Notes |
|---|---|---|
| Fan (main entity) | 2.1 on, 2.4 mode, 9.11 favorite level | Presets `auto` / `sleep` / `favorite`; setting a speed switches to Favorite at level 1–14 |
| Mode (select) | 2.4 | Same as the fan preset |
| PM2.5 | 3.4 | µg/m³ |
| Filter life | 4.1 | % |
| Filter time left | 4.4 | days |
| Filter used time | 4.3 | hours, diagnostic |
| Motor speed | 9.1 | rpm, diagnostic |
| Fault | 2.2 | `no_fault` / `motor_stuck` / `sensor_lost` |
| Child lock (switch) | 8.1 | |
| Button beep (switch) | 6.1 | |
| Favorite level (number) | 9.11 | 0–14 |
| Screen brightness (select) | 13.2 | `off` / `dim` / `bright` (spec: Close / Bright / Brightness) |
| Reset filter (button) | action 4.1 | Use after a filter change |

Not exposed on purpose: 9.10 country-code (changing the region can lock the device to another cloud), 9.12 debug filter time, 11.4 AQI heartbeat. The firmware answers `"hello"` for every device-information property (siid 1), so the MAC address from `miIO.info` is the unique id.

## Installation

1. HACS → Custom repositories → `https://github.com/scr34m/ha-xiaomi-air-purifier-4-compact`, category **Integration**, then download it and restart. Or manually: copy `custom_components/xiaomi_air_purifier_4_compact` into `config/custom_components/` of Home Assistant, then restart.
2. Settings → Devices & services → Add integration → **Xiaomi Smart Air Purifier 4 Compact**.
3. Enter the IP address and the 32-character token (from the Xiaomi Cloud Tokens Extractor). Add each purifier separately.

Disable any other integration polling the same purifier (xiaomi_miio, Xiaomi Miot Auto) to avoid miIO message id conflicts.

Debug logging:

```yaml
logger:
  logs:
    custom_components.xiaomi_air_purifier_4_compact: debug
    miio: info
```

## Tests

```sh
pip install pytest-homeassistant-custom-component python-miio
pytest                       # unit tests, mocked device
PURIFIER_HOST=<ip> PURIFIER_TOKEN=<token> pytest tests_live -s   # real device, no-op writes only
```

Verified on two devices, firmware `2.2.10_0021`, with Home Assistant 2026.10.4.
