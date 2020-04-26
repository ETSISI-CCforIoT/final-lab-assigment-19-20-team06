import json
import asyncio
import logging

CMD_RESPONSE_CODE = [
    ('OK', 'Command processed successfully'),
    ('E01', 'JSON Bad deserialization'),
    ('E02', 'Command not found'),
    ('E03', 'Components not in arguments'),
    ('E04', 'Component {} not in component list'),
    ('E05', 'Argument {} not found'),
    ('E06', 'Bad {} argument, expected: {}, received: {}'),
    ('E07', 'Command RPC not received'),
    ('E08', 'Connection refused from SIM SERVER')
]

FE_SERVER_HOST = '127.0.0.1'
FE_SERVER_PORT = 8888

SIM_SERVER_HOST = '127.0.0.1'
SIM_SERVER_PORT = 8887


def compose_packet(addr, status, stmsg, **kwargs):
    packet = {
        'id': addr[0]+":"+str(addr[1]),
        'status': status,
        'st_msg': stmsg
    }
    packet.update(**kwargs)
    return packet


def get_comp(addr, request):
    """Get a component
        @param addr:    Address tuple (IP, PORT)
        @param request: string of the component ID
    """
    try:
        name = request['arguments']
        components = json.load(open('comps.json', 'r'))
        if name not in components:
            packet = compose_packet(addr, CMD_RESPONSE_CODE[4][0], CMD_RESPONSE_CODE[4][1].format(name))
        else:
            packet = compose_packet(addr,
                                    CMD_RESPONSE_CODE[0][0],
                                    CMD_RESPONSE_CODE[0][1],
                                    flow=components[name][2],
                                    units='L/min')
    except KeyError:
        packet = compose_packet(addr, CMD_RESPONSE_CODE[3][0], CMD_RESPONSE_CODE[3][1])
    return packet


async def set_comp(addr, request):
    """Set a component
        @param addr:    Address tuple (IP, PORT)
        @param request: Dictionary with structure {'c_name': str_component_id,
                                                   'c_comp': [float_ddp, float_res, float_cur]}
    """
    try:
        args = request['arguments']
        components = json.load(open('comps.json', 'r'))
        if 'c_name' not in args:
            packet = compose_packet(addr, CMD_RESPONSE_CODE[5][0], CMD_RESPONSE_CODE[5][1].format('c_name'))
        elif 'c_values' not in args:
            packet = compose_packet(addr, CMD_RESPONSE_CODE[5][0], CMD_RESPONSE_CODE[5][1].format('c_values'))
        elif len(args['c_values']) != 3:
            packet = compose_packet(addr,
                                    CMD_RESPONSE_CODE[6][0],
                                    CMD_RESPONSE_CODE[6][1].format('c_values',
                                                                   3,
                                                                   len(args['c_values'])))
        elif args['c_name'] not in components:
            packet = compose_packet(addr, CMD_RESPONSE_CODE[4][0], CMD_RESPONSE_CODE[4][1].format(args['c_name']))
        else:
            await frontend_client(json.dumps(request))
            packet = compose_packet(addr, CMD_RESPONSE_CODE[0][0], CMD_RESPONSE_CODE[0][1])
    except KeyError:
        packet = compose_packet(addr, CMD_RESPONSE_CODE[3][0], CMD_RESPONSE_CODE[3][1])
    except ConnectionRefusedError:
        packet = compose_packet(addr, CMD_RESPONSE_CODE[8][0], CMD_RESPONSE_CODE[8][1])
    return packet


def load_data(addr, request):
    """Load components data from simulator
        @param addr:    Address tuple (IP, PORT)
        @param request: List with structure [{'comp_a_id': , [float_ddp_a, float_res_a, float_cur_a]},
                                             ...
                                             {'comp_N_id': , [float_ddp_N, float_res_N, float_cur_N]}]
    """
    try:
        components = request['arguments']
        packet = compose_packet(addr, CMD_RESPONSE_CODE[0][0], CMD_RESPONSE_CODE[0][1])
        json.dump(components, open('comps.json', 'w'))
    except KeyError:
        packet = compose_packet(addr, CMD_RESPONSE_CODE[3][0], CMD_RESPONSE_CODE[3][1])
    return packet


async def command_processor(addr, request):
    """Process any received command or command error or command not fount and generates a packet."""
    packet = None
    command = None
    try:
        command = request['command']
        if command == 'getComp':
            packet = get_comp(addr, request)
        elif command == 'setComp':
            packet = await set_comp(addr, request)
        elif command == 'loadData':
            packet = load_data(addr, request)
        elif command == 'jsonERROR':
            packet = compose_packet(addr, CMD_RESPONSE_CODE[1][0], CMD_RESPONSE_CODE[1][1])
        else:
            packet = compose_packet(addr, CMD_RESPONSE_CODE[2][0], CMD_RESPONSE_CODE[2][1])
    except KeyError:
        packet = compose_packet(addr, CMD_RESPONSE_CODE[7][0], CMD_RESPONSE_CODE[7][1])
    await asyncio.sleep(0.1)
    return packet, command


async def frontend_server_handler(reader, writer):
    logger = logging.getLogger('SERVER_LOG')
    data = await reader.read(2048)
    message = data.decode()
    addr = writer.get_extra_info('peername')

    try:
        request = json.loads(message)
    except json.decoder.JSONDecodeError:
        request = {'command': 'jsonERROR'}

    packet, command = await command_processor(addr, request)

    response = json.dumps(packet).encode('utf-8')
    writer.write(response)
    await writer.drain()

    logger.info('[%s_%s] Response: %s', addr, command, response)

    logger.info('Close the connection')
    writer.close()


async def frontend_server():
    local_server = await asyncio.start_server(frontend_server_handler, FE_SERVER_HOST, FE_SERVER_PORT)
    address = local_server.sockets[0].getsockname()
    logging.getLogger('SERVER_LOG').info('Serving on %s', address)

    async with local_server:
        await local_server.serve_forever()


async def frontend_client(raw_sm):
    rdr, wtr = await asyncio.open_connection(SIM_SERVER_HOST, SIM_SERVER_PORT)
    wtr.write(raw_sm.encode())
    data = await rdr.read(100)
    wtr.close()
    await asyncio.sleep(1)


async def main():
    await asyncio.create_task(frontend_server())

logging.basicConfig(level=logging.INFO)

loop = asyncio.get_event_loop()

try:
    loop.run_until_complete(main())
except KeyboardInterrupt:
    loop.stop()
