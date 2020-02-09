[![License](https://img.shields.io/github/license/mikelawrence/senseme-hacs)](LICENSE) [![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

# Home Assistant SenseME fan and light

The Haiku with SenseME fan is a WiFi connected fan and installable light from Big Ass Fans. This component provides control of these fans and light using Home Assistant.

## Installation

### Manual

Copy the custom_components folder to your own hassio config folder.

### HACS

Click on Settings in Home Assistant Community Store. Add this repository ```https://github.com/mikelawrence/hacs-senseme``` to Custom Repositories as an Integration.

## Configuration

The Haiku with SenseME fan component will automatically discover and create a fan and light for each discovered fan. See next paragraph to prevent the light from being added if you don't have one. Setting ```max_number_fans:``` to the number of Haiku fans on your network will speed up the discovery process but is not required. If ```include:``` is specified, discovered fans with a matching name will be added. If ```exclude:``` is specified, discovered fans with a matching name will NOT be added. If both ```include:``` and ```exclude:``` are specified, only ```include:``` will be honored. If neither ```include:``` and ```exclude:``` are specified, all auto-detected fans will be added.

For included fans you can specify a ```friendly_name``` to use instead of ```name``` in Home Assistant. This is handy for grouped fans. Controlling any fan in a group will affect all fans of that group. Default value is the same as ```name```. Also new in the include section is the ```has_light``` boolean which when ```true``` will add a light component along with the fan. The default for ```has_light``` is ```true```. The included fan section must have a ```name``` variable and it must must match the name in the Haiku app.

```yaml
# enable Haiku with SenseMe ceiling fans
senseme:
  max_number_fans: 2
  # used to include only specific fans
  include:
    - name: "Studio Vault Fan"
      friendly_name: "Studio Fan"
      has_light: false
    - name: "Family Room Fan"
  # or use exclude to prevent specific auto-detected fan
  exclude:
    - "Studio Beam Fan"
```

## Credits

Thanks to TomFaulkner and his [SenseMe](https://github.com/TomFaulkner/SenseMe) python library. This library does the real work in controlling the Big Ass Fans.

## Problems

* Occasionally changes to the fan state fail to connect to fan and make the change, usually as a network (python socket) error. Same thing is true for the SenseMe background task which gets the complete fan state every minute.
* Originally the Senseme custom component auto-detected both the existence of a light and the fan's group but longer term usage showed a problem with consistently auto-detecting these values. This version no longer auto-detects these values and requires the user to specify them in advance.
