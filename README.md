# Canberra garbage collection integration for Home Assistant.

Canberra garbage collection integration utilising the ACT Gov Data website.
You will need:

- The name of the desired pickup suburb

## Installation

This component current only supports manual installation.
- Place this directory in `/config/custom_components`. If `custom_components`
  does not exist, you will have to create it.
- Add the sensor to your configuration.yaml:

```yaml
sensor:
  - platform: canberragarbage
    name: [name]
    suburb: [suburb]
```
- Verify that the custom entities are available in home assistant (Garbage,
  Recycling and Greenwaste).

## Multiple Locations

If you have multiple locations you wish to track, add another sensor with a new
name:

```yaml
sensor:
  - platform: canberragarbage
    name: [name 2]
    suburb: [suburb 2]
```
## Documentation

Documentation for the API can be found on the SolaxCloud website:
https://dev.socrata.com/foundry/www.data.act.gov.au/jzzy-44un
