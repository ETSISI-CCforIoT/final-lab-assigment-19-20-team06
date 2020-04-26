import asyncio
import json
import logging

FE_SERVER_HOST = '127.0.0.1'
FE_SERVER_PORT = 8888

CLIENT_ID = 'WATER_IN_1'

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


async def main():
    ## Init mqtt client
    
    while True:
        try:
            reader, writer = await tcp_connect()
            packet = {
                'command': 'getComp',
                'arguments': CLIENT_ID
            }
            await tcp_send_package(reader, writer, json.dumps(packet))
            await tcp_close(writer)

            ##mqtt.publish

            await asyncio.sleep(5)
        except ConnectionRefusedError:
            logger = logging.getLogger(CLIENT_ID)
            logger.info('Connection Refused to %s:%d', FE_SERVER_HOST, FE_SERVER_PORT)

logging.basicConfig(level=logging.INFO)

loop = asyncio.get_event_loop()

try:
    loop.run_until_complete(main())
except KeyboardInterrupt:
    loop.stop()