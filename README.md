# Bookoo Scale Integration

This is a Home Assistant integration for the BOOKOO Bluetooth scale. It provides sensors for weight, flow rate, timer, and other scale metrics along with controls for configuration.

Based on the documentation at https://github.com/BooKooCode/OpenSource/

## Features

### Sensors
- Weight (g)
- Flow rate (g/s)
- Timer (s)
- Battery level (%)
- Standby time (minutes)
- Current beep level (0-5)
- Flow smoothing status (ON/OFF)
- Current weight unit

### Controls
- Tare
- Start/Stop timer
- Reset timer
- Tare and start timer
- Adjust beep level (0-5)
- Set auto-off timer (1-30 minutes)
- Toggle flow smoothing

## Installation

1. Add this repository to HACS.
2. Your Bookoo Themis scale should be automatically discovered by Home Assistant
