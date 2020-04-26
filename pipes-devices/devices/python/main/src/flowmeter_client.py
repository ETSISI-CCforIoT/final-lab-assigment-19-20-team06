import asyncio
import time
import json
import logging
import paho.mqtt.client as mqtt

MQTT_BROKER_IP = '127.0.0.1'
MQTT_BROKER_PORT = 1883
MQTT_BROKER_TOPIC = 'floors/floor1/data'

FE_SERVER_HOST = '127.0.0.1'
FE_SERVER_PORT = 8888

# TODO CLIENT_ID and PIPE_ID can be the same if the names in the simulator match with names in the cloud
CLIENT_ID = 'PIPE_1_S1'
PIPE_ID = 'pipe1-sensor1'
REFRESH_PERIOD = 5


async def tcp_connect():
    logger = logging.getLogger(CLIENT_ID)
    rdr, wtr = await asyncio.open_connection(FE_SERVER_HOST, FE_SERVER_PORT)
    logger.info('Open the connection')
    return rdr, wtr


async def tcp_send_package(rdr, wtr, package):
    logger = logging.getLogger(CLIENT_ID)
    logger.info('Send: %s', package)
    wtr.write(package.encode())

    data = await rdr.read(1024)
    logger.info('Received: %s', data.decode())
    return data


async def tcp_close(wtr):
    logger = logging.getLogger(CLIENT_ID)
    logger.info('Close the connection')
    wtr.close()


async def main(mqtt_client):
    
    while True:
        try:
            reader, writer = await tcp_connect()
            packet = {
                'command': 'getComp',
                'arguments': CLIENT_ID
            }
            raw_response = await tcp_send_package(reader, writer, json.dumps(packet))
            await tcp_close(writer)

            response = json.loads(raw_response)
            if response['status'] == 'OK':
                mqtt_client.publish(MQTT_BROKER_TOPIC, payload=compose_packet(response['flow'], response['units']))

            await asyncio.sleep(REFRESH_PERIOD)
        except ConnectionRefusedError:
            logger = logging.getLogger(CLIENT_ID)
            logger.info('Connection Refused to %s:%d', FE_SERVER_HOST, FE_SERVER_PORT)


def on_connect(client, userdata, flags, rc):
    logger = logging.getLogger(CLIENT_ID+"_MQTT")
    logger.info('Connected to %s:%d with code %s', MQTT_BROKER_IP, MQTT_BROKER_PORT, rc)


def on_disconnect(client, userdata, rc, properties):
    logger = logging.getLogger(CLIENT_ID+"_MQTT")
    logger.info('Disconnected from %s:%d with code %s', MQTT_BROKER_IP, MQTT_BROKER_PORT, rc)


def compose_packet(flow, unit):
    packet = {
        "id": PIPE_ID,
        "flow": round(flow, 4),
        "unit": unit,
        "timestamp": time.time()
    }
    return json.dumps(packet)


logging.basicConfig(level=logging.INFO)
MQTT_CLIENT = mqtt.Client(client_id=CLIENT_ID)

MQTT_CLIENT.on_connect = on_connect
MQTT_CLIENT.on_disconnect = on_disconnect

MQTT_CLIENT.connect(MQTT_BROKER_IP, port=MQTT_BROKER_PORT)
MQTT_CLIENT.loop_start()

LOOP = asyncio.get_event_loop()

try:
    LOOP.run_until_complete(main(MQTT_CLIENT))
except KeyboardInterrupt:
    LOOP.stop()
    MQTT_CLIENT.loop_stop()
    MQTT_CLIENT.disconnect()
