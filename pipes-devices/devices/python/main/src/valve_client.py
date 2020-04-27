"""
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@                              @@@@@,@@@@@@@@@@@%/%@@@@@@@@@@@,@@@@@@@&&@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@    VALVE SIMULATE DEVICE     @                                   @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@                              @                                   @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@  · Patricia Gómez            @@@(   ,@@@@@@@       @@@@@@@*   ,@@@@@@@@@@@@@@@@&&@@@@@@@@@@@@@@@@
@@  · Dharma Lancelot Martínez  @@@@@@@@@@@@@           @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@  · Mario Refoyo              @@@@@@@@@        (          @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@  · Pablo Barreda             @@@@@@@@@@                 @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@  · Carlos Medina             @@@@@@@@@@                 @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@                              @@@@@@@@                    *@@@@@@@@@@@@@@@      (&@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@*                                          @        @@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@                                               @        @@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@    /                                              @        @@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@                                                     @        @@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@             @@@@@@@@@                  @@@@@@@@@@@@@@@@.      @@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@            @@@@@@@@@@@@@@(          @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@            @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@          * @@@@                                                               @@
@@@@@@@@@@@@@@@@@@@@@@@ @@@@@@@@@@@                                                               @@
@@@@@@@@@@@@@@@@@@@@@@*  @@@@@@@@@@                                                               @@
@@@@@@@@@@@@@@@@@@@@@     @@@@@@@@@                                                               @@
@@@@@@@@@@@@@@@@&@@         @@@@@@@   Implementation  of a valve device which instead of make an  @@
@@@@@@@@@@@@@@@@@.            @@@@@  action directly to  a real pipe, it requests  the action to  @@
@@@@@@@@@@@@@@@@@           @  @@@@  update a component value to a simulator frontend server.     @@
@@@@@@@@@@@@@@@@@           @ ,@@@@                                                               @@
@@@@@@@@@@@@@@@@@@        /// @@@@@                                                               @@
@@@@@@@@@@@@@@@@@@@@   ,/( @@@@@@@@                                                               @@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                                                               @@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
----------------------------------------------------------------------------------------------------
"""
import asyncio
import json
import logging
import random
import paho.mqtt.client as mqtt

random.seed()

MQTT_BROKER_IP = '127.0.0.1'
MQTT_BROKER_PORT = 1883
MQTT_BROKER_TOPIC = 'floors/floor1/alarms'

FE_SERVER_HOST = '127.0.0.1'
FE_SERVER_PORT = 8888

CLIENT_ID = 'WATER_IN_1'
CURRENT_VALUE = 100.0


async def tcp_connect():
    logger = logging.getLogger(CLIENT_ID)
    rdr, wtr = await asyncio.open_connection(FE_SERVER_HOST, FE_SERVER_PORT)
    logger.info('Open the connection')
    return rdr, wtr


async def tcp_send_package(rdr, wtr, package):
    logger = logging.getLogger(CLIENT_ID)
    logger.info('Send: %s', package)
    wtr.write(package.encode())

    data = await rdr.read(100)
    logger.info('Received: %s', data.decode())


async def tcp_close(wtr):
    logger = logging.getLogger(CLIENT_ID)
    logger.info('Close the connection')
    wtr.close()


async def main():  # global CURRENT_VALUE reader function
    global CURRENT_VALUE
    logger = logging.getLogger(CLIENT_ID+"_MQTTVALVE")
    logger.info('Press Ctrl-C to exit...')
    previous_val = CURRENT_VALUE
    while True:
        if previous_val != CURRENT_VALUE:
            try:
                reader, writer = await tcp_connect()
                packet = {
                    'command': 'setComp',
                    'arguments': {
                                   'c_name': CLIENT_ID,
                                   'c_values': [CURRENT_VALUE, 0.0, 1.0]
                                  }
                }
                await tcp_send_package(reader, writer, json.dumps(packet))
                await tcp_close(writer)

                previous_val = CURRENT_VALUE

                await asyncio.sleep(1)
            except ConnectionRefusedError:
                logger = logging.getLogger(CLIENT_ID)
                logger.info('Connection Refused to %s:%d', FE_SERVER_HOST, FE_SERVER_PORT)


def on_connect(client, userdata, flags, rc):
    logger = logging.getLogger(CLIENT_ID+"_MQTTVALVE")
    logger.info('Connected to %s:%d with code %s', MQTT_BROKER_IP, MQTT_BROKER_PORT, rc)
    client.subscribe(MQTT_BROKER_TOPIC)


def on_disconnect(client, userdata, rc, properties):
    logger = logging.getLogger(CLIENT_ID+"_MQTTVALVE")
    logger.info('Disconnected from %s:%d with code %s', MQTT_BROKER_IP, MQTT_BROKER_PORT, rc)


def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    logger = logging.getLogger(CLIENT_ID+"_MQTTVALVE")
    logger.info('Subscribed with mid %s', mid)

# TODO Put the data from payload as new CURRENT_VALUE


def on_message(client, userdata, message):  # global CURRENT_VALUE writer function
    global CURRENT_VALUE
    logger = logging.getLogger(CLIENT_ID + "_MQTTVALVE")
    logger.info('-'*30)
    logger.info('\t topic: %s', message.topic)
    logger.info('\t payload: %s', message.payload)
    logger.info('\t qos: %d ', message.qos)
    temp = float(random.randint(0, 5)) * 10.0 + 50.0
    logger.info('PUMP: SET PUMP %s POWER TO %s', CLIENT_ID, temp)
    CURRENT_VALUE = temp
    logger.info('-'*30)


logging.basicConfig(level=logging.INFO)
MQTT_CLIENT = mqtt.Client(client_id=CLIENT_ID)

MQTT_CLIENT.on_connect = on_connect
MQTT_CLIENT.on_disconnect = on_disconnect
MQTT_CLIENT.on_message = on_message
MQTT_CLIENT.on_subscribe = on_subscribe

MQTT_CLIENT.connect(MQTT_BROKER_IP, port=MQTT_BROKER_PORT)
MQTT_CLIENT.loop_start()

LOOP = asyncio.get_event_loop()

try:
    LOOP.run_until_complete(main())
except KeyboardInterrupt:
    LOOP.stop()
    MQTT_CLIENT.loop_stop()
    MQTT_CLIENT.disconnect()
