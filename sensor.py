# Library imports
import json
import requests
import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from datetime import timedelta
from datetime import datetime

from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle
from homeassistant.components.sensor import PLATFORM_SCHEMA

# Frequency of data retrieval
MIN_TIME_BETWEEN_UPDATES = timedelta(hours=6)

CONF_NAME = "name"
CONF_SUBURB = "suburb"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_SUBURB): cv.string
    }
)

# Set up the SolaxCloud platform
def setup_platform(hass, config, add_entities, discovery_info=None):
    collection = Collection(hass, config[CONF_NAME], config[CONF_SUBURB])
    # Add the sensors to the platform
    add_entities([GarbageDateSensor(hass, collection),
                  RecyclingDateSensor(hass, collection),
                  GreenwasteDateSensor(hass, collection),
                  GarbageDaysSensor(hass, collection),
                  RecyclingDaysSensor(hass, collection),
                  GreenwasteDaysSensor(hass, collection)
                  ], True)

# Calculate the number of days until the next collection date
def calculate_days(collection_date):
    myDate = datetime.strptime(collection_date, "%d/%m/%Y")
    remainingDays = (myDate - datetime.today()).days

    if(remainingDays == 0):
        return 'Today'
    elif(remainingDays == 1):
        return 'Tomorrow'
    else:
        return str(remainingDays) + ' days'

class Collection:
    def __init__(self, hass, name, suburb):
        self.hass = hass
        self.logger = logging.getLogger(__name__)
        self.suburb = suburb.upper()
        self.name = name
        self.data = {}
        self.uri = f'https://www.data.act.gov.au/resource/jzzy-44un.json?suburb={suburb}'
        self.last_data_time = None

    # Retrieve data from API access point
    def get_data(self):
        # If there is no data, or the data needs to be updated
        if not self.data or datetime.now() - self.last_data_time > MIN_TIME_BETWEEN_UPDATES:
            try:
                data = requests.get(self.uri).json()
                if data:
                    self.data = data[0]
                    self.last_data_time = datetime.now()
                    self.logger.info(
                        f'Retrieved new data from ACT Data for {self.name}')
                else:
                    self.data = {}
                    self.logger.error(f'Failed to retrieve new data from ACT Data for {self.name}')
            except requests.exceptions.ConnectionError as e:
                self.logger.error(str(e))
                self.data = {}

# The date of the next garbage bin collection
class GarbageDateSensor(Entity):
    def __init__(self, hass, collection):
        self._name = collection.name + ' Garbage Date'
        self.hass = hass
        self.collection = collection

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        data = self.collection.data['garbage_pickup_date']
        return float('nan') if data is None else data

    @property
    def icon(self):
        return 'mdi:calendar'

    @property
    def friendly_name(self):
        return 'Next Garbage Collection'

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        self.collection.get_data()

# The data of the net recycling bin collection
class RecyclingDateSensor(Entity):
    def __init__(self, hass, collection):
        self._name = collection.name + ' Recycling Date'
        self.hass = hass
        self.collection = collection

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        data = self.collection.data['recycling_pickup_date']
        return float('nan') if data is None else data

    @property
    def icon(self):
        return 'mdi:calendar'

    @property
    def friendly_name(self):
        return 'Next Recycling Collection'

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        self.collection.get_data()

# The date of the next greenwaste bin collection
class GreenwasteDateSensor(Entity):
    def __init__(self, hass, collection):
        self._name = collection.name + ' Greenwaste Date'
        self.hass = hass
        self.collection = collection

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        data = self.collection.data['next_greenwaste_date']
        return float('nan') if data is None else data

    @property
    def icon(self):
        return 'mdi:calendar'

    @property
    def friendly_name(self):
        return 'Next Greenwaste Collection'

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        self.collection.get_data()

# The number of remaining days until garbage collection
class GarbageDaysSensor(Entity):
    def __init__(self, hass, collection):
        self._name = collection.name + ' Garbage Days'
        self.hass = hass
        self.collection = collection

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        data = self.collection.data['garbage_pickup_date']
        data = calculate_days(data)
        return float('nan') if data is None else data

    @property
    def icon(self):
        return 'mdi:calendar'

    @property
    def friendly_name(self):
        return 'Days until garbage collection'

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        self.collection.get_data()

# The number of remaining days until recycling collection
class RecyclingDaysSensor(Entity):
    def __init__(self, hass, collection):
        self._name = collection.name + ' Recycling Days'
        self.hass = hass
        self.collection = collection

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        data = self.collection.data['recycling_pickup_date']
        data = calculate_days(data)
        return float('nan') if data is None else data

    @property
    def icon(self):
        return 'mdi:calendar'

    @property
    def friendly_name(self):
        return 'Days until recycling collection'

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        self.collection.get_data()

# The number of remaining days until greenwaste collection
class GreenwasteDaysSensor(Entity):
    def __init__(self, hass, collection):
        self._name = collection.name + ' Greenwaste Days'
        self.hass = hass
        self.collection = collection

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        data = self.collection.data['next_greenwaste_date']
        data = calculate_days(data)
        return float('nan') if data is None else data

    @property
    def icon(self):
        return 'mdi:calendar'

    @property
    def friendly_name(self):
        return 'Days until greenwaste collection'

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        self.collection.get_data()
