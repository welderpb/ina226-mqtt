#!/usr/bin/env python3
import logging
from ina226 import INA226
from time import sleep
import os

import paho.mqtt.publish as publish

# Config from environment (see Dockerfile)
BUSNUM    = int(os.getenv('BUSNUM', '1'))
MAXEXAMPS = int(os.getenv('MAX_EXPECTED_AMPS', '1')) 

MQTT_SERVICE_HOST = os.getenv('MQTT_SERVICE_HOST', 'mosquitto.local')
MQTT_SERVICE_PORT = int(os.getenv('MQTT_SERVICE_PORT', 1883))
MQTT_SERVICE_USER = os.getenv('MQTT_SERVICE_USER', None)
MQTT_SERVICE_PASSWORD = os.getenv('MQTT_SERVICE_PASSWORD', None)
MQTT_SERVICE_TOPIC = os.getenv('MQTT_SERVICE_TOPIC', 'home/livingroom')
MQTT_CLIENT_ID = os.getenv('MQTT_CLIENT_ID', os.getenv('HOSTNAME'))
HA_NAME = os.getenv('HA_NAME', None)

def read():
    print("Bus Voltage    : %.3f V" % ina.voltage())
    print("Bus Current    : %.3f mA" % ina.current())
    print("Supply Voltage : %.3f V" % ina.supply_voltage())
    print("Shunt voltage  : %.3f mV" % ina.shunt_voltage())
    print("Power          : %.3f mW" % ina.power())


if __name__ == "__main__":
    MQTT_SERVICE_AUTH = None

    if MQTT_SERVICE_USER is not None:
        MQTT_SERVICE_AUTH = {'username':MQTT_SERVICE_USER, 'password':MQTT_SERVICE_PASSWORD}

    if HA_NAME is not None:
        volt_config = '''{
          "state_topic": "INA226/%(HA_NAME)s/voltage",
          "icon": "mdi:power-plug",
          "name": "%(HA_NAME)s Bus Voltage",
          "unique_id": "ina226_%(HA_NAME)s_voltage",
          "unit_of_measurement": "V",
          "device": {
             "identifiers": ["%(HA_NAME)s"],
             "manufacturer": "Texas Instruments",
             "model": "INA226",
             "name": "%(HA_NAME)s"
          }
        }'''
        cur_config = '''{
          "state_topic": "INA226/%(HA_NAME)s/current",
          "icon": "mdi:current-dc",
          "name": "%(HA_NAME)s Current",
          "unique_id": "ina226_%(HA_NAME)s_current",
          "unit_of_measurement": "mA",
          "device": {
             "identifiers": ["%(HA_NAME)s"],
             "manufacturer": "Texas Instruments",
             "model": "INA226",
             "name": "%(HA_NAME)s"
          }
        }'''

        # Prepare sensors config to be published on MQTT
        cfgs = [(f"homeassistant/sensor/INA226/{HA_NAME}_voltage/config", volt_config % {"HA_NAME": HA_NAME}),
                (f"homeassistant/sensor/INA226/{HA_NAME}_current/config", cur_config % {"HA_NAME": HA_NAME})]
        MQTT_SERVICE_TOPIC = f"INA226/{HA_NAME}"

    ina = INA226(busnum=BUSNUM, max_expected_amps=MAXEXAMPS, log_level=logging.INFO)
    ina.configure()
    ina.set_low_battery(5)
    sleep(3)
    print("===================================================Begin to read")
    read()
    sleep(2)
    '''
    print("===================================================Begin to reset")
    ina.reset()
    sleep(5)
    ina.configure()
    ina.set_low_battery(3)
    sleep(5)
    print("===================================================Begin to sleep")
    ina.sleep()
    sleep(2)
    print("===================================================Begin to wake")
    ina.wake()
    sleep(0.2)
    print("===================================================Read again")
    read()
    sleep(5)
    print("===================================================Trigger test")
    '''
    ina.wake(3)
    sleep(0.2)
    while True:
        ina.wake(3)
        sleep(3)
        while 1:
            if ina.is_conversion_ready():
                sleep(3)
                print("===================================================Conversion ready")
                read()
                try:
                    # Prepare messages to be published on MQTT
                    msgs = [(f"{MQTT_SERVICE_TOPIC}/voltage", ina.voltage()), (f"{MQTT_SERVICE_TOPIC}/current", ina.current())]

                    # Publish messages on given MQTT broker
                    logger.info("Sending sensor config.")
                    publish.multiple(cfgs, hostname=MQTT_SERVICE_HOST, port=MQTT_SERVICE_PORT, client_id=MQTT_CLIENT_ID, auth=MQTT_SERVICE_AUTH)
                    logger.info("Sending sensor data.")
                    publish.multiple(msgs, hostname=MQTT_SERVICE_HOST, port=MQTT_SERVICE_PORT, client_id=MQTT_CLIENT_ID, auth=MQTT_SERVICE_AUTH)
                except Exception:
                    logger.error("An error occured publishing values to MQTT", exc_info=True)

                break
        sleep(1)
        print("===================================================Trigger again")
