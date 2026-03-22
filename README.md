<p align="center">
  <img src="https://biqu.equipment/cdn/shop/files/1_b6f16f3b-9be2-46e1-ae3d-a31be8abdfaf.jpg?v=1736227118&width=600" alt="BIQU Panda Breath" width="500"/>
</p>

<h1 align="center">🐼 Panda Breath for Home Assistant</h1>

<p align="center">
  <a href="https://github.com/hacs/integration"><img src="https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge" alt="HACS Custom"/></a>
  <img src="https://img.shields.io/badge/version-1.0.0-blue?style=for-the-badge" alt="Version"/>
  <img src="https://img.shields.io/badge/HA-2023.6+-brightgreen?style=for-the-badge&logo=homeassistant" alt="Home Assistant"/>
  <img src="https://img.shields.io/badge/protocol-WebSocket-yellow?style=for-the-badge" alt="WebSocket"/>
  <img src="https://img.shields.io/badge/cloud-free-success?style=for-the-badge" alt="No Cloud"/>
</p>

<p align="center">
  <b>Control your BIQU Panda Breath directly from Home Assistant.</b><br/>
  No cloud. No MQTT. Pure local WebSocket.
</p>

---

## 🌡️ What is Panda Breath?

The **BIQU Panda Breath** is a smart 3-in-1 device for Bambu Lab and Klipper printers:
- **300W PTC Chamber Heater** — reduces warping for ABS, ASA, PC, PA
- **HEPA + Carbon Air Filter** — captures VOCs and fine particles
- **Filament Dryer** — dries spools when the printer is idle

This integration brings full local control of the Panda Breath into Home Assistant — with real-time temperature, automations, and no dependency on any cloud service.

---

## ✨ Features

| Feature | Description |
|--------|-------------|
| 🔌 **Power Switch** | Turn the device on or off |
| ⚙️ **Work Mode** | Switch between Auto, Power On, Filament Drying |
| 🎯 **Target Temperature** | Set chamber target temperature (25–60°C) |
| 💨 **Filter Threshold** | Set filter fan activation threshold |
| 🔥 **Heater Threshold** | Set heater activation threshold |
| 🌡️ **Chamber Temperature** | Real-time sensor updated every few seconds |
| 🔍 **Auto Discovery** | Finds the device automatically via mDNS |
| 🔁 **Auto Reconnect** | Handles IP changes and reconnects automatically |
| 📡 **100% Local** | Communicates via WebSocket — no cloud, no MQTT |

---

## 📦 Installation

### Via HACS (recommended)

1. Open **HACS** in Home Assistant
2. Go to **Integrations**
3. Click ⋮ → **Custom repositories**
4. Add `https://github.com/mikigua/ha-panda-breath` as **Integration**
5. Search for **Panda Breath** and click **Download**
6. **Restart** Home Assistant

### Manual

1. Download or clone this repository
2. Copy the `custom_components/panda_breath` folder to your HA `config/custom_components/` directory
3. **Restart** Home Assistant

---

## ⚙️ Configuration

After installation and restart:

1. Go to **Settings → Devices & Services**
2. Click **+ Add Integration**
3. Search for **Panda Breath**
4. The device will be **auto-discovered** if it's on the same network as Home Assistant
5. Or enter the hostname/IP manually (default: `pandabreath.local`)

---

## 📊 Entities

| Entity | Type | Description |
|--------|------|-------------|
| `switch.panda_breath_power` | Switch | Turn the device on/off |
| `select.panda_breath_work_mode` | Select | Auto / Power On / Filament Drying |
| `number.panda_breath_target_chamber_temperature` | Number | Target temperature (25–60°C) |
| `number.panda_breath_filter_fan_activation_threshold` | Number | Filter fan threshold (0–120°C) |
| `number.panda_breath_heater_activation_threshold` | Number | Heater threshold (40–120°C) |
| `sensor.panda_breath_chamber_temperature` | Sensor | Current chamber temperature (real-time) |
| `sensor.panda_breath_firmware_version` | Sensor | Firmware version |

---

## 🤖 Automation Examples

### Start heating when a print begins

```yaml
automation:
  - alias: "Panda Breath - Start on print"
    trigger:
      - platform: state
        entity_id: sensor.bambu_p1s_print_status
        to: "printing"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.panda_breath_power
      - service: select.select_option
        target:
          entity_id: select.panda_breath_work_mode
        data:
          option: "Auto"
```

### Switch to drying mode when print finishes

```yaml
automation:
  - alias: "Panda Breath - Dry filament after print"
    trigger:
      - platform: state
        entity_id: sensor.bambu_p1s_print_status
        to: "idle"
    action:
      - service: select.select_option
        target:
          entity_id: select.panda_breath_work_mode
        data:
          option: "Filament Drying"
```

---

## 🔧 Requirements

- **Panda Breath firmware** V1.0.2 or newer
- **Home Assistant** 2023.6 or newer
- Panda Breath and Home Assistant on the **same local network**

---

## 🛠️ How It Works

This integration communicates directly with the Panda Breath via **WebSocket** (`ws://pandabreath.local/ws`):

- On startup, connects and reads the full device state
- Keeps a persistent connection to receive **real-time chamber temperature** updates
- Reconnects every 60 seconds to refresh all settings
- Sends commands via the same WebSocket channel

The protocol was reverse-engineered from the Panda Breath web UI firmware.

---

## 🐛 Issues & Contributing

Found a bug or have a feature request? Open an issue on [GitHub](https://github.com/mikigua/ha-panda-breath/issues).

Pull requests are welcome!

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">
  Made with ❤️ for the Home Assistant and 3D printing community<br/>
  <i>Not affiliated with BIQU / BigTreeTech</i>
</p>



[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

Home Assistant integration for the **BIQU Panda Breath** — smart chamber heater, air filter, and filament dryer for Bambu Lab and Klipper 3D printers.

## Features

- 🌡️ **Real-time chamber temperature** sensor (updates every few seconds)
- 🔌 **Power switch** — turn the device on/off
- ⚙️ **Work mode** selector — Auto / Power On / Filament Drying
- 🎯 **Target chamber temperature** — adjustable 25–60°C
- 💨 **Filter fan activation threshold** — adjustable 0–120°C
- 🔥 **Heater activation threshold** — adjustable 40–120°C
- 🔄 **Auto-discovery** via mDNS (`pandabreath.local`)
- 🔁 **Auto-reconnect** if the device IP changes

## Installation via HACS

1. Open HACS in Home Assistant
2. Go to **Integrations**
3. Click the three dots (⋮) → **Custom repositories**
4. Add `https://github.com/mikigua/ha-panda-breath` as **Integration**
5. Search for **Panda Breath** and install it
6. Restart Home Assistant

## Manual Installation

1. Copy the `custom_components/panda_breath` folder to your HA `config/custom_components/` directory
2. Restart Home Assistant

## Configuration

After installation:

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for **Panda Breath**
3. The device will be auto-discovered if it's on the same network, or you can enter the hostname/IP manually

## Requirements

- Panda Breath firmware **V1.0.2** or newer
- Home Assistant **2023.6** or newer
- The Panda Breath must be on the same local network as Home Assistant

## Entities

| Entity | Type | Description |
|--------|------|-------------|
| `switch.panda_breath_power` | Switch | Turn the device on/off |
| `select.panda_breath_work_mode` | Select | Auto / Power On / Filament Drying |
| `number.panda_breath_target_chamber_temperature` | Number | Target temperature (25–60°C) |
| `number.panda_breath_filter_fan_activation_threshold` | Number | Filter fan threshold (0–120°C) |
| `number.panda_breath_heater_activation_threshold` | Number | Heater threshold (40–120°C) |
| `sensor.panda_breath_chamber_temperature` | Sensor | Current chamber temperature |
| `sensor.panda_breath_firmware_version` | Sensor | Firmware version (hidden by default) |

## Protocol

This integration communicates directly with the Panda Breath via **WebSocket** (`ws://pandabreath.local/ws`) — no cloud, no MQTT broker required. Everything is local.

## Credits

Protocol reverse-engineered from the Panda Breath web UI firmware.
