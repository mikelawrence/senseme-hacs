# Changelog for Home Assistant integration for SenseME fans

## 2.2.3 - Bump aiosenseme library to >= v.5.4

* This improves detection logic for lost connections to devices.

## 2.2.2 - Add additional controls

* Sleep Mode is now a separate switch instead of a preset mode.
* Added Motion switch for fans and lights. Home Assistant can enable/disable SenseME's automatic control of devices when occupancy is detected.
* Thanks go to [bdraco](https://github.com/bdraco) for these changes!

## 2.2.1 - Improve documentation for existing users

* No functional changes.

## 2.2.0 - Support new fan model in Home Assistant

* Support the new fan model in Home Assistant 2021.3. Speed is now based on percentage. Whoosh has changed to a preset mode and now Sleep is also available as a preset mode. Let me know if this works for your use case!
* Senseme Device can now be added by IP address instead of requiring discovery first. Some users prefer to isolate their IoT devices on a separate network. Discovery uses UDP broadcast packets which by design do not traverse through routers. Now these users will be able to still control their Haiku devices.
* There are substantial changes to the integration's config flow. Previously, devices were discovered and all were added to Home Assistant. Now discovered devices are suggestions to what the user may want to add to Home Assistant. Here you can type in an IP address for a device that cannot be discovered. Each device is now added separately.
* Once devices are added to Home Assistant they are remembered between restarts and discovery is not required to reconnect. Sometimes discovery doesn't work and so a reboot could cause a device to disappear from Home Assistant until rediscovered and sometimes they just don't respond to requests from the LAN. If this happens on Home Assistant restart the previously added devices will still show up but as unavailable.
* Since whoosh is now a preset mode instead of hidden behind oscillate functionality there was no real need for integrations options so they have been removed.
* Bump version aiosenseme >= v0.5.2.
* Sorry but translations have been lost in this release.
* Thanks go to [bdraco](https://github.com/bdraco) for all the great help in improving this release!

## 2.1.3 - Add Norwegian translation. Thanks [hwikene](https://github.com/hwikene)

* Support [aiosenseme v0.4.4](https://pypi.org/project/aiosenseme/0.4.4/). No functional changes for this integration.

## 2.1.2 - Fix missing occupancy sensor for Standalone Haiku Light

## 2.1.1 - Support occupancy sensor in Haiku L fans with Wireless Wall Controller

* Haiku L Fans will report occupancy status if connected to a Wireless Wall Controller. This version attempts to detect a occupancy sensor in Haiku L Fans but it may not work correctly. So for those who have a Haiku L Fan and no Wireless Wall Sensor please check that NO occupancy sensor appears in Home Assistant and please create a new issue on [GitHub](https://github.com/mikelawrence/senseme-hacs/issues) to tell me it's working or not.

## 2.1.0 - Support standalone Haiku Light

* Haiku Light supports brightness, color temp and occupancy sensor. Kudos to [PenitentTangent2401](https://github.com/mikelawrence/senseme-hacs/issues/7) for his assistance in testing and debugging these changes.

## 2.0.10 - Fix problems caused by 2.0.9

* Removed changes in 2.0.9 that caused problems for some users. No changes to integration functionality.
* Requires Home Assistant 0.110 or higher.

## 2.0.9 - Fix new depreciations in Home Assistant

* Fix under the hood depreciations in Home Assistant 0.110. No changes to integration functionality.
* Requires Home Assistant 0.109 or higher.

## 2.0.8 - Adjust to new requirements in Home Assistant

* Move '.translations' directory to 'translations'. No changes to integration functionality.
* Now requires Home Assistant 0.109 or higher.

## 2.0.7 - Fix L-Series Fans and Wall Controller problems

* Haiku L-Series fans no longer have an occupancy sensor.
* Ignore Wireless Wall Controllers by using [aiosenseme v0.3.3](https://pypi.org/project/aiosenseme/0.3.3/).

## 2.0.6 - Support aiosenseme update

* Support changes in [aiosenseme v0.3.2](https://pypi.org/project/aiosenseme/0.3.2/).

## 2.0.5 - Add configuration options

* Added 'Enable Whoosh as Oscillate' configuration option.
* Added 'Enable Direction' configuration option.

## 2.0.4 - Support aiosenseme update

* Support API changes in aiosenseme v0.3.1.
* Cleanup pylint warnings.

## 2.0.3 - Support aiosenseme update

* Support API changes in aiosenseme v0.2.0.

## 2.0.2 - Fix L-Series unknown model error

* Fix light and occupancy sensor for L-Series Haiku fans and unknown models.

## 2.0.1 - Fix L-Series unknown model error

* Added L-Series Haiku fan to list of known models.
* Unknown models are now added with a warning instead of being ignored.

## 2.0.0 - New asynchronous library

* Now a HACS default integration.
* [Breaking Change] Configuration via Home Assistant frontend only.
* Supports fan, light and occupancy binary_sensor platforms.
* Fan status is pushed for more or less instantaneous updates.
* Uses my [aiosenseme library](https://pypi.org/project/aiosenseme/) to control fans and get status. This library is designed from the ground up to support Home Assistant.
* Supports **asyncio** see [Asynchronous Programming](https://developers.home-assistant.io/docs/asyncio_index).

## 1.0.0 - First HACS version

* SenseME now supports HACS custom install.
* Supported fan and light platforms.
* Uses [SenseMe library](https://pypi.org/project/SenseMe/) to control fans.
* Polling is used to get the status of the fan which was problematic and sluggish.
