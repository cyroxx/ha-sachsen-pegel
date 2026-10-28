# Sachsen Pegel for Home Assistant

Custom integration for Home Assistant that provides water levels of the Saxon gauge stations (HWIMS) via the [Sachsen Pegel Proxy](https://sachsen-pegel-proxy.vercel.app).

## Sensors per station

| Sensor | Unit | Note |
| --- | --- | --- |
| Water level | cm | |
| Flow | m³/s | |
| Flood alert level | – | Text, passed through from the source in German (e.g. "Kein Hochwasser"); not translated |
| Alarm level | – | Numeric (0–4), derived from the flood alert level text. `0` means no alarm; `unknown` if the station has no flood alert function (`Kein Hochwassermeldepegel`) or the text could not be parsed. Carries the official alarm thresholds (in cm) as attributes `alarm_threshold_1_cm` … `alarm_threshold_4_cm`, when known |
| Last measurement | – | Timestamp of the latest measurement |

Values are fetched every 5 minutes. If a value is missing in the source, the sensor is `unknown`.

## Installation

### HACS (custom repository)

1. Open HACS, top-right menu, **Custom repositories**.
2. Enter the repository URL, category **Integration**.
3. Install "Sachsen Pegel" and restart Home Assistant.

### Manual

Copy `custom_components/sachsen_pegel` to `<config>/custom_components/` and restart Home Assistant.

## Setup

**Settings → Devices & services → Add integration → Sachsen Pegel**. First enter the proxy base URL (default: `https://sachsen-pegel-proxy.vercel.app`), then select the gauge station. Add the integration again for each additional station.

## Flood alert blueprint

This repository ships a ready-to-use automation blueprint that notifies when a
station's alarm level crosses a configurable threshold (hysteresis: it fires
once when entering and once when leaving the alarm range, not on every
intermediate state change). No manual cm thresholds or helper entities are
required — the blueprint uses the `Alarm level` sensor above directly.

[![Open your Home Assistant instance and show the blueprint import dialog with a specific blueprint pre-filled.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fraw.githubusercontent.com%2Fcyroxx%2Fha-sachsen-pegel%2Fmain%2Fblueprints%2Fautomation%2Fcyroxx%2Fhochwasser-alarm.yaml)

Or manually: **Settings → Automations & scenes → Blueprints → Import blueprint**
and paste:

```text
https://raw.githubusercontent.com/cyroxx/ha-sachsen-pegel/main/blueprints/automation/cyroxx/hochwasser-alarm.yaml
```

Then create an automation from the blueprint, select the station's `Alarm level`
sensor, optionally the `Water level`/`Flow` sensors for the notification text,
a notify target, and the alarm level threshold (1–4).

## Disclaimer

Availability and accuracy of the data are not guaranteed. This project is not affiliated with the Free State of Saxony.

