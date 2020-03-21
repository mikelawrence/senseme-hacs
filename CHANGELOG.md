# HACS version of the Home Assistant SenseME integration

## 2.0.0 - New asynchronous library

* [Breaking Change] Configuration via Home Assistant frontend only.
* Supports fan, light and occupancy binary_sensor platforms.
* Fan status is pushed for more or less instantaneous updates.
* Uses my [aiosenseme library](https://pypi.org/project/aiosenseme/) to control fans and get status. This library is designed from the ground up to support Home Assistant.
* Supports **asyncio** see [Asynchronous Programming](https://developers.home-assistant.io/docs/asyncio_index).

## 1.0.0 - First HACS version

* Supported fan and light platforms.
* Uses [SenseMe library](https://pypi.org/project/SenseMe/) to control fans.
* Polling is used to get the status of the fan which was problematic and sluggish.
