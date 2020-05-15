## SenseME integration

The Haiku with SenseME fan is a WiFi connected fan and optional light from Big Ass Fans. This Home Assistant integration provides control of these fans and light.

* Requires Home Assistant 0.109.0 or greater.
* This integration is currently NOT compatible with the [i6 fan](https://www.bigassfans.com/fans/i6/).
* This integration is currently NOT compatible with the discontinued [Wireless Wall Control](https://www.bigassfans.com/docs/haiku/accessories/cutsheet-haiku-wall-control.pdf).

### Features

* Confirmed support of Haiku, Haiku H, and Haiku L fans.
* Probably supports Haiku C fans. If you have a Haiku C fan you should be seeing a warning about an unknown model in the Home Assistant log. Please open an issue [here](https://github.com/mikelawrence/senseme-hacs/issues) to let me know the model name.
* Configuration via Home Assistant frontend.
* Fan supports speed, direction and whoosh as oscillate.
* Light supported if installed.
* Occupancy sensor supported.
* Control of any one fan in a room (Haiku App configured) affects all fans in that room.

### Usage

* Go to **Configuration -> Integrations**.
* Click on the **+** in the bottom right corner to add a new integration.
* Search and select **SenseME** integration from the list.
* Click the **Submit** button on the popup window. The SenseME component will automatically detect SenseME fans on the network and setup a fan, light (if installed) and an occupancy sensor.

### Options

There are two global options available: **Enable Direction** and **Enable Whoosh as Oscillate**. With **Enable Direction** you can enable fan direction control for all SenseME fans in Home Assistant. **Enable Whoosh as Oscillate** allows you to control Haiku Fan Whoosh mode via Home Assistant's built-in Oscillate control. To change options follow the instructions below.

* Go to **Configuration -> Integrations -> SenseME**
* Click the gear icon at the top right.
