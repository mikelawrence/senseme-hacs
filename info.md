## SenseME integration

{% if installed %}
{% if version_installed.replace("v", "").replace(".","") | int < 220  %}
> **Important Note: The SenseME integration has had significant changes to the way devices are handled. Previously just adding the integration enabled discovery and would automatically add all found devices to Home Assistant. This is no longer the case. Now you add the SenseME integration for each device you would like Home Assistant to control. You will need to remove the existing SenseME integration from Home Assistant before adding your devices one at a time as discussed below in the Configuration section. It doesn't matter if you remove the integration before or after upgrading the SenseME integration via HACS.**
{% endif %}
{% endif %}

The Haiku with SenseME fan is a WiFi connected fan and optional light from Big Ass Fans (BAF). This integration gives Home Assistant the ability to control these fans and lights. The occupancy sensor is also monitored if present. BAF made a standalone Haiku light for a while that is also compatible with this integration.

Be sure to setup your devices with the Haiku by BAF app before using this integration.

> * **Important Note: If your device uses the Big Ass Fans app, like the i6 or es6 fans, I'm sorry to say that this integration won't work for you.**

### Features

* Confirmed support of Haiku, Haiku H, and Haiku L fans.
* Confirmed support of stand alone Haiku Light.
* Supports [Wireless Wall Control](https://www.bigassfans.com/support/haiku-wireless-wall-control/) indirectly through fan status reporting.
* Probably supports Haiku C fans. If you have a Haiku C fan you might be seeing a warning about an unknown model in the Home Assistant log. Please open an issue [here](https://github.com/mikelawrence/senseme-hacs/issues) to let me know the model name.
* Haiku Fan supports speed, direction, light and occupancy sensor if available.
* Haiku Fan whoosh and sleep modes are available as preset modes.
* Haiku Light supports brightness, color temp and occupancy sensor.
* Adding just one of the devices in a room will allow Home Assistant to control all of them.

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

Selected Version {{ selected_tag }}
