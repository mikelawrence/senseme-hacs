## SenseME integration

The Haiku with SenseME fan is a WiFi connected fan and optional light from Big Ass Fans. This Home Assistant integration provides control of these fans and light.

### Features

* Supports Haiku and Haiku L fans.
* Configuration via Home Assistant frontend.
* Fan supports speed, direction and whoosh as oscillate.
* Light supported if installed.
* Occupancy sensor supported.
* Control of any one fan in a room (Haiku App configured) affects all fans in the room.

### Usage

* Go to **Configuration -> Integrations**.
* Click on the **+** in the bottom right corner to add a new integration.
* Search and select **SenseME** integration from the list.
* Click the **Submit** button on the popup window. The SenseME component will automatically detect SenseME fans on the network and setup a fan, light (if installed) and an occupancy sensor.

### Options

There are two global options available: **Enable Direction** and **Enable Whoosh as Oscillate**. **Enable Direction** is pretty obvious but the **Enable Whoosh as Oscillate** allows you to control Haiku Fan Whoosh mode via Home Assistant's built-in Oscillate fan control. To change options follow the instructions below.

* Go to **Configuration -> Integrations -> SenseME**
* Click the gear icon at the top right.
