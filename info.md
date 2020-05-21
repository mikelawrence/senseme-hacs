## SenseME integration

The Haiku with SenseME fan is a WiFi connected fan and optional light from Big Ass Fans. This Home Assistant integration provides control of these fans and light.

* Requires Home Assistant 0.110.0 or greater.
* This integration is currently NOT compatible with the [i6 fan](https://www.bigassfans.com/fans/i6/).
* This integration is currently NOT compatible with the discontinued [Wireless Wall Control](https://www.bigassfans.com/docs/haiku/accessories/cutsheet-haiku-wall-control.pdf).

### Features

* Confirmed support of Haiku, Haiku H, and Haiku L fans.
* Probably supports Haiku C fans. If you have a Haiku C fan you should be seeing a warning about an unknown model in the Home Assistant log. Please open an issue [here](https://github.com/mikelawrence/senseme-hacs/issues) to let me know the model name.
* Configuration via Home Assistant frontend.
* Fan supports speed, direction, whoosh as oscillate, light if installed and occupancy sensor if available.
* Haiku Light supports brightness, color temp and occupancy sensor.
* Control of any one device in a room (Haiku App configured) affects all devices in that room.

### Usage

* Go to **Configuration -> Integrations**.
* Click on the **+** in the bottom right corner to add a new integration.
* Search and select **SenseME** integration from the list.
* Click the **Submit** button on the popup window. The SenseME component will automatically detect SenseME fans on the network and setup a fan, light (if installed) and an occupancy sensor.

### Options

There are two global options available: **Enable Direction** and **Enable Whoosh as Oscillate**. With **Enable Direction** you can enable fan direction control for all SenseME fans in Home Assistant. **Enable Whoosh as Oscillate** allows you to control Haiku Fan Whoosh mode via Home Assistant's built-in Oscillate control. To change options follow the instructions below.

* Go to **Configuration -> Integrations -> SenseME**
* Click the gear icon at the top right.

### Issues

* Unknown models will produce a warning 'Discovered unknown SenseME device model' in Home Assistant. If you get this warning post an issue on [GitHub](https://github.com/mikelawrence/senseme-hacs/issues) with the model detected and I'll add that model to stop the warning.
* Sometimes SenseME fans just don't respond to discovery packets. It happens enough for me to mention it here. You will have to keep trying to add the SenseME integration until at least one fan is detected. From there all fans will be eventually detected by the periodic discovery built-in to the integration. If your fans are grayed out when you restart Home Assistant it just means the initial discovery didn't detect them but again the periodic discovery will eventually detect them.
* SenseME fans will occasionally drop the connection to Home Assistant. The integration will detect this and automatically reconnect. If it was the fan that dropped the connection this integration will usually reconnect within a minute. I'm not sure why but if the fan is powered off it can take a long time to detect the lost connection and that time varies based on what platform Home Assistant Core is running. On my development platform (Windows Subsystem for Linux running Ubuntu) a powered off fan is detected in a couple of minutes. Home Assistant running on a Raspberry Pi takes upwards of 25 minutes to detect lost connections.

### Debugging

To aid in debugging you can add the following to your configuration.yaml file. Be sure not to duplicate the ```logger:``` section.

```yaml
logger:
  default: warning
  logs:
    custom_components.senseme: debug
    aiosenseme: debug
    aiosenseme.discovery: debug
```
