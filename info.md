## SenseME integration

**Important Note: The SenseME integration has had significant changes to the way devices are handled. Previously just adding the integration enabled discovery and would automatically add all found devices to Home Assistant. This is no longer the case. Now you add the SenseME integration for each device you would like Home Assistant to control.**

**For existing users of this integration your previous devices will not exist when you update to this version v2.2.0. All you should need to do is follow the instructions in the Configuration section below to add them back.**

The Haiku with SenseME fan is a WiFi connected fan and optional light from Big Ass Fans (BAF). This Home Assistant integration provides control of these fans and light. The occupancy sensor is also monitored if present. BAF made a standalone light for a while that is also compatible with this integration.

If your fan uses the "Haiku by BAF" app there is a good chance your device can be controlled by this integration. Your luck runs out if the device you are trying to control uses the "Big Ass Fans" app.

### Features

* Confirmed support of Haiku, Haiku H, and Haiku L fans.
* Confirmed support of stand alone Haiku Light.
* Supports [Wireless Wall Control](https://www.bigassfans.com/support/haiku-wireless-wall-control/) indirectly through fan status reporting.
* Probably supports Haiku C fans. If you have a Haiku C fan you might be seeing a warning about an unknown model in the Home Assistant log. Please open an issue [here](https://github.com/mikelawrence/senseme-hacs/issues) to let me know the model name.
* Configuration via Home Assistant frontend.
* Haiku Fan supports speed, direction, light and occupancy sensor if available.
* Whoosh and sleep modes are available as preset modes.
* Haiku Light supports brightness, color temp and occupancy sensor.
* Control of any one device in a room (BAF App configured) affects all devices in that room. This is a feature of the devices not this integration.

### Configuration

1. Go to **Configuration -> Integrations**.
2. Click on the **+ ADD INTEGRATION** button in the bottom right corner.
3. Search for and select the `SenseME` integration.

   <img src="https://raw.githubusercontent.com/mikelawrence/senseme-hacs/master/img/search.png"/>

4. If any devices are discovered you will see the dialog below. Select a discovered device and click `Submit` and you are done. If you would prefer to add a device by IP address select that option, click `Submit`, and you will be presented with the dialog in step 5.

   <img src="https://raw.githubusercontent.com/mikelawrence/senseme-hacs/master/img/device.png"/>

5. If no devices were discovered or you selected the `IP Address` option the dialog below is presented. Here you can type in an IP address of undiscoverable devices.

   <img src="https://raw.githubusercontent.com/mikelawrence/senseme-hacs/master/img/address.png"/>

6. Repeat these steps for each device you wish to add.

### SenseME platforms

When the integration connects to a device it retrieves the *Device Name* you set in the Haiku by BAF app and uses that as a prefix for all created entities.

* For fans you get the following platforms:
  * `fan` named "*Device Name*".
    * Supports On/Off.
    * Supports Speed percentage that snaps to possible speeds, usually 7 not including off.
    * Supports Directions Forward and Reverse.
    * Supports Preset Modes Whoosh and Sleep.
  * `light` (if it exists) named "*Device Name* Light".
    * Supports Brightness percentage that snaps to possible levels usually 16 not including off.
  * `binary_sensor` (if it exists) named "*Device Name* Occupancy".
    * Device class is occupancy.
* For lights you get the following platforms:
  * `light` named "*Device Name*".
    * Supports Brightness percentage that snaps to possible light brightness levels usually 16 not including off.
    * Supports Color Temp.
  * `binary_sensor` named "*Device Name* Occupancy".
    * Device class is occupancy.

### Senseme platform attributes

* All platforms: (fan, light and binary_sensor)
  * `room_name`: When the device is associated in a group of devices this will be the name of the room. All devices in the group will have the same name for `room_name`. `room_name` will be *"EMPTY* if the device is not in a room.
  * `room_type`: When the device is associated in a group of devices this will be the type of room. All fans in the group will have the same `room_type`. There 29 room types: *"Undefined"*, *"Other"*, *"Master Bedroom"*, *"Bedroom"*, *"Den"*, *"Family Room"*, *"Living Room"*, *"Kids Room"*, *"Kitchen"*, *"Dining Room"*, *"Basement"*, *"Office"*, *"Patio"*, *"Porch"*, *"Hallway"*, *"Entryway"*, *"Bathroom"*, *"Laundry"*, *"Stairs"*, *"Closet"*, *"Sunroom"*, *"Media Room"*, *"Gym"*, *"Garage"*, *"Outside"*, *"Loft"*, *"Playroom"*, *"Pantry"* and *"Mudroom"*
* Fan platform
  * `auto_comfort`: Auto Comfort allows the fan to monitor and adjust to room conditions like temperature, humidity and occupancy. There are four possible states: *"Off"*, *"Cooling"*, *"Heating"*, and *"Followtstat"*.
  * `smartmode`: Smartmode indicates the fan's comfort mode. When `auto_comfort` is set to *"Followtstat"* the actual `auto_comfort` value will change based the connected thermostat otherwise `smartmode` tracks `auto_comfort`. There are three possible states: *"Off"*, *"Cooling"* and *"Heating"*.
  * `motion_control`: is *"On"* when the fan is controlled by the occupancy sensor, *"Off"* otherwise.
* Light platform
  * `motion_control`: is *"On"* when the light is controlled by the occupancy sensor, *"Off"* otherwise.

### Issues

* This integration is NOT compatible with the [i6 fan](https://www.bigassfans.com/fans/i6/). This probably applies to the [es6 fan](https://www.bigassfans.com/fans/es6/) as well but it has not been tested.
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
