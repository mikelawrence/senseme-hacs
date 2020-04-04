# Changelog for Home Assistant integration for SenseME fans

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
