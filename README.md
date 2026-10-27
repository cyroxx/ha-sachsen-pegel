# Sachsen Pegel for Home Assistant

Custom integration for Home Assistant that provides water levels of the Saxon gauge stations (HWIMS) via the [Sachsen Pegel Proxy](https://github.com/cyroxx/sachsen-pegel-proxy).

## Sensors per station

| Sensor | Unit | Note |
| --- | --- | --- |
| Water level | cm | |
| Flow | m³/s | |
| Flood alert level | – | Text, passed through from the source in German (e.g. "Kein Hochwasser"); not translated |
| Last measurement | – | Timestamp of the latest measurement |

Values are fetched every 15 minutes. If a value is missing in the source, the sensor is `unknown`.

## Installation

### HACS (custom repository)

1. Open HACS, top-right menu, **Custom repositories**.
2. Enter the repository URL, category **Integration**.
3. Install "Sachsen Pegel" and restart Home Assistant.

### Manual

Copy `custom_components/sachsen_pegel` to `<config>/custom_components/` and restart Home Assistant.

## Setup

**Settings → Devices & services → Add integration → Sachsen Pegel**. First enter the proxy base URL (default: `https://sachsen-pegel-proxy.vercel.app`), then select the gauge station. Add the integration again for each additional station.

## Disclaimer

Availability and accuracy of the data are not guaranteed. This project is not affiliated with the Free State of Saxony.
