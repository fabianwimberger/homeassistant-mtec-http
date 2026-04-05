# Testing with a Fresh Home Assistant Instance

This guide walks through setting up a clean Home Assistant instance to test the M-TEC integration without touching your production environment.

## Prerequisites

- Docker installed
- Your M-TEC heat pump reachable on the local network
- This repo cloned locally

## 1. Start a Fresh Home Assistant Container

```bash
docker run -d \
  --name ha-test \
  --network host \
  -v /tmp/ha-test-config:/config \
  ghcr.io/home-assistant/home-assistant:stable
```

Using `--network host` so the container can reach the heat pump on your LAN. The config lives in `/tmp/ha-test-config` and can be thrown away after testing.

## 2. Install the Integration

Copy the custom component into the container's config:

```bash
mkdir -p /tmp/ha-test-config/custom_components
cp -r custom_components/mtec /tmp/ha-test-config/custom_components/
```

Restart the container to pick up the new integration:

```bash
docker restart ha-test
```

## 3. Set Up the Integration

1. Open `http://localhost:8123` in your browser
2. Complete the onboarding (create a user, skip location/integrations)
3. Go to **Settings > Devices & Services > Add Integration**
4. Search for **M-TEC Heat Pump**
5. Enter your heat pump's IP address (e.g. `192.168.1.100`)
6. Set scan interval (15s is a good default)

## 4. What to Verify

### Entities created

- Go to **Settings > Devices & Services > M-TEC Heat Pump** and click the device
- Check that only entities matching your hardware appear (no phantom circuits)
- Sensors should show live values, not "unavailable"

### Climate thermostats

- Open one of the HC climate entities
- Verify current temperature and target temperature are populated
- Try switching HVAC mode (Off/Auto/Heat) and presets (Day/Night)
- Confirm the change reflects on the heat pump's own display

### Number controls

- Find the day/night temperature number entities
- Adjust a value and verify it updates on the heat pump

### Select controls

- Change the system operating mode or hot water mode
- Verify the new mode is reflected

### Diagnostics

- Go to the integration page, click the three dots, **Download diagnostics**
- Open the JSON and check:
  - `signals.available` lists your probed signals
  - `signals.unavailable` lists signals your unit doesn't support
  - `data` contains current sensor values

### Energy dashboard

- Go to **Settings > Dashboards > Energy**
- Add **Total heating energy** and **Total electrical energy** as consumption sensors
- Verify they appear with `total_increasing` state class

### Options flow

- On the integration card, click **Configure**
- Change the scan interval to 60s
- Verify the integration reloads and continues working

### Reconfigure flow

- On the integration card, click the three dots > **Reconfigure**
- Enter a different (invalid) IP, confirm you get a "cannot connect" error
- Enter the correct IP again, confirm it works

## 5. Cleanup

```bash
docker stop ha-test && docker rm ha-test
rm -rf /tmp/ha-test-config
```
