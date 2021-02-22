## SenseME integration

The Haiku with SenseME fan is a WiFi connected fan and optional light from Big Ass Fans. This Home Assistant integration provides control of these fans and light.

* Requires Home Assistant 2021.3 or greater.
* This integration is currently NOT compatible with the [i6 fan](https://www.bigassfans.com/fans/i6/).

### Features

* Confirmed support of Haiku, Haiku H, and Haiku L fans.
* Confirmed support of stand alone Haiku Light.
* Supports [Wireless Wall Control](https://www.bigassfans.com/support/haiku-wireless-wall-control/) indirectly through fan status reporting.
* Probably supports Haiku C fans. If you have a Haiku C fan you might be seeing a warning about an unknown model in the Home Assistant log. Please open an issue [here](https://github.com/mikelawrence/senseme-hacs/issues) to let me know the model name.
* Configuration via Home Assistant frontend.
* Haiku Fan supports speed, direction, light and occupancy sensor if available.
* Whoosh and sleep modes are available as present modes.
* Haiku Light supports brightness, color temp and occupancy sensor.
* Control of any one device in a room (BAF App configured) affects all devices in that room. This is a feature of the devices not this integration.

### Usage

1. Go to **Configuration -> Integrations**.
2. Click on the **+** in the bottom right corner to add a new integration.
3. Search and select **SenseME** integration from the list.
4. The SenseME integration will attempt to discover SenseME devices on the network and offer a list of available devices for you to add to Home Assistant. You can use a device name but only if it show in the list of available devices. For devices that cannot be discovered simply type in the IP address. Click the **Submit** button to add the device to Home Assistant.
5. Repeat steps 2 - 4 for each device you want to add to Home Assistant.

### Senseme platform attributes

* All platforms: (fan, light and binary_sensor)
  * **room_name**: When the device is associated in a group of devices this will be the name of the room. All devices in the group will have the same name for **room_name**. **room_name** will be *EMPTY* if the device is not in a room.
  * **room_type**: When the device is associated in a group of devices this will be the type of room. All fans in the group will have the same **room_type**. There 29 room types: *Undefined*, *Other*, *Master Bedroom*, *Bedroom*, *Den*, *Family Room*, *Living Room*, *Kids Room*, *Kitchen*, *Dining Room*, *Basement*, *Office*, *Patio*, *Porch*, *Hallway*, *Entryway*, *Bathroom*, *Laundry*, *Stairs*, *Closet*, *Sunroom*, *Media Room*, *Gym*, *Garage*, *Outside*, *Loft*, *Playroom*, *Pantry* and *Mudroom*
* Fan platform
  * **auto_comfort**: Auto Comfort allows the fan to monitor and adjust to room conditions like temperature, humidity and occupancy. There are four possible states: *Off*, *Cooling*, *Heating*, and *Followtstat*.
  * **smartmode**: When **auto_comfort** is set to *Followtstat* the actual **auto_comfort** mode will change based the connected thermostat. When **auto_comfort** is NOT set to *Followtstat* **smartmode** tracks **auto_comfort**.There are three possible states: *Off*, *Cooling* and *Heating*.
  * **motion_control**: is *On* when the fan is controlled by the occupancy sensor, *Off* otherwise.
* Light platform
  * **motion_control**: is *On* when the light is controlled by the occupancy sensor, *Off* otherwise.

### Issues

* This integration is currently NOT compatible with the [i6 fan](https://www.bigassfans.com/fans/i6/).
* Unknown models will produce a warning 'Discovered unknown SenseME device model' in the Home Assistant log. If you get this warning post an issue on [GitHub](https://github.com/mikelawrence/senseme-hacs/issues) with the model detected and I'll try add that model to stop the warning. Unknown models are treated as fans; this may cause problems.
* The occupancy sensor is treated differently than other devices settings/states; occupancy state changes are not pushed immediately and must be detected with periodic status updates. This will make updates to the occupancy sensor sluggish. This sensor in my two fans is also erratic. They tend to detect occupancy when there is no one present including pets.
* Sometimes SenseME devices just don't respond to discovery packets. If you are trying to add the device you can simply use the IP address or you can try a again later when the SenseME devices are more cooperative.
* SenseME fans will occasionally drop the connection to Home Assistant. The integration will detect this and automatically reconnect. If it was the fan that dropped the connection this integration will usually reconnect within a minute. I'm not sure why but if the fan is powered off it can take a long time to detect the lost connection and that time varies based on what platform Home Assistant Core is running. On my development platform (Windows Subsystem for Linux running Ubuntu) a powered off fan is detected in a couple of minutes. Home Assistant running on a Raspberry Pi takes upwards of 25 minutes to detect lost connections.

### Debugging

To aid in debugging you can add the following to your configuration.yaml file. Be sure not to duplicate the ```logger:``` section.

```yaml
logger:
  default: warning
  logs:
    custom_components.senseme: debug
    aiosenseme.device: debug
    aiosenseme.discovery: debug
```
