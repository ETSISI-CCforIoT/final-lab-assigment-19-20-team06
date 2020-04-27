"""
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@                              @@@@@,@@@@@@@@@@@%/%@@@@@@@@@@@,@@@@@@@&&@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@   SIMULATOR BACKEND SERVER   @                                   @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
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
@@@@@@@@@@@@@@@@@@@@@@*  @@@@@@@@@@    Simulator   process   backend.  Launch   the   simulation  @@
@@@@@@@@@@@@@@@@@@@@@     @@@@@@@@@  periodically  and  update  the component  values.  The  new  @@
@@@@@@@@@@@@@@@@&@@         @@@@@@@  information  is  sent  to the frontend to serve  with  this  @@
@@@@@@@@@@@@@@@@@.            @@@@@  information to any client device.                            @@
@@@@@@@@@@@@@@@@@           @  @@@@                                                               @@
@@@@@@@@@@@@@@@@@           @ ,@@@@  Edit define_simulator(sm) function to match to your pipe or  @@
@@@@@@@@@@@@@@@@@@        /// @@@@@  circuit configuration.                                       @@
@@@@@@@@@@@@@@@@@@@@   ,/( @@@@@@@@                                                               @@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                                                               @@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
----------------------------------------------------------------------------------------------------
"""
import json
import asyncio
import logging
import argparse
import circuit

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--front-host", type=str, help="Frontend host IPv4 address")
parser.add_argument("-p", "--front-port", type=int, help="Frontend host TCP port")
parser.add_argument("-b", "--back-host", type=str, help="Backend host IPv4 address")
parser.add_argument("-g", "--back-port", type=int, help="Backend host IPv4 address")

args = parser.parse_args()

SIM_SERVER_HOST = '127.0.0.1' if args.back_host is None else args.back_host
SIM_SERVER_PORT = 8887 if args.back_port is None else args.back_port

FE_SERVER_HOST = '127.0.0.1' if args.front_host is None else args.front_host
FE_SERVER_PORT = 8888 if args.front_port is None else args.front_port

SIM = circuit.Simulator()

CMD_RESPONSE_CODE = [
    ('OK', 'Command processed successfully'),
    ('E01', 'JSON Bad deserialization'),
    ('E02', 'Command not found'),
    ('E03', 'Components not in arguments'),
    ('E04', 'Component {} not in component list'),
    ('E05', 'Argument {} not found'),
    ('E06', 'Bad {} argument'),
    ('E07', 'Command RPC not received')
]


def define_simulator(sm):
    sm.register_component('WATER_IN_1', circuit.PowerSrc(ddp=100))
    sm.register_component('PIPE_1_S1', circuit.Transducers(res=1))
    sm.register_component('PIPE_1_S2', circuit.Transducers(res=1))
    sm.register_component('PIPE_1_S3', circuit.Transducers(res=1))
    sm.register_component('PIPE_1_S4', circuit.Transducers(res=1))
    sm.register_component('PIPE_1_S5', circuit.Transducers(res=1))
    sm.register_component('PIPE_1_S6', circuit.Transducers(res=1))
    sm.register_component('PIPE_2_S1', circuit.Transducers(res=1))
    sm.register_component('PIPE_4_S1', circuit.Transducers(res=1))
    sm.register_component('PIPE_3_S1', circuit.Transducers(res=1))
    sm.register_component('PIPE_3_S2', circuit.Transducers(res=1))
    sm.register_component('PIPE_4_S2', circuit.Transducers(res=1))
    sm.register_component('PIPE_2_S2', circuit.Transducers(res=1))
    sm.register_component('TAP_1', circuit.Transducers(res=1))
    sm.register_component('TAP_2', circuit.Transducers(res=1))
    sm.register_component('TAP_3', circuit.Transducers(res=1))

    sm.connect(sm.get_component('WATER_IN_1').one, sm.get_component('PIPE_1_S1').one)
    sm.connect(sm.get_component('PIPE_1_S1').two, sm.get_component('PIPE_1_S2').one)
    sm.connect(sm.get_component('PIPE_1_S2').two, sm.get_component('PIPE_1_S3').one)
    sm.connect(sm.get_component('PIPE_1_S3').two, sm.get_component('PIPE_1_S4').one)
    sm.connect(sm.get_component('PIPE_1_S4').two, sm.get_component('PIPE_1_S5').one)
    sm.connect(sm.get_component('PIPE_1_S5').two, sm.get_component('PIPE_1_S6').one)
    sm.connect(sm.get_component('PIPE_1_S6').two, sm.get_component('PIPE_2_S1').one)
    sm.connect(sm.get_component('PIPE_2_S1').two, sm.get_component('PIPE_2_S2').one)
    sm.connect(sm.get_component('PIPE_2_S2').two, sm.get_component('TAP_1').one)
    sm.connect(sm.get_component('TAP_1').two, sm.get_component('WATER_IN_1').two)
    sm.connect(sm.get_component('PIPE_1_S6').two, sm.get_component('PIPE_3_S1').one)
    sm.connect(sm.get_component('PIPE_3_S1').two, sm.get_component('PIPE_3_S2').one)
    sm.connect(sm.get_component('PIPE_3_S2').two, sm.get_component('TAP_2').one)
    sm.connect(sm.get_component('TAP_2').two, sm.get_component('WATER_IN_1').two)
    sm.connect(sm.get_component('PIPE_1_S6').two, sm.get_component('PIPE_4_S1').one)
    sm.connect(sm.get_component('PIPE_4_S1').two, sm.get_component('PIPE_4_S2').one)
    sm.connect(sm.get_component('PIPE_4_S2').two, sm.get_component('TAP_3').one)
    sm.connect(sm.get_component('TAP_3').two, sm.get_component('WATER_IN_1').two)

    sm.reference = sm.get_component('WATER_IN_1').two


def compose_packet(addr, status, stmsg, **kwargs):
    packet = {
        'id': addr[0]+":"+str(addr[1]),
        'status': status,
        'st_msg': stmsg
    }
    packet.update(**kwargs)
    return packet

def set_comp(addr, request):
    """Set a component
        @param addr:    Address tuple (IP, PORT)
        @param request: Dictionary with structure {'c_name': str_component_id,
                                                   'c_comp': [float_ddp, float_res, float_cur]}
    """
    global SIM
    try:
        args = request['arguments']
        SIM.get_component(args['c_name']).ddp = args['c_values'][0]
        SIM.get_component(args['c_name']).res = args['c_values'][1]
        SIM.get_component(args['c_name']).cur = args['c_values'][2]
        packet = compose_packet(addr, CMD_RESPONSE_CODE[0][0], CMD_RESPONSE_CODE[0][1])
    except KeyError:
        packet = compose_packet(addr, CMD_RESPONSE_CODE[3][0], CMD_RESPONSE_CODE[3][1])
    return packet

def command_processor(addr, request):
    """Process any received command or command error or command not fount and generates a packet."""
    packet = None
    command = None
    try:
        command = request['command']
        if command == 'setComp':
            packet = set_comp(addr, request)
        elif command == 'jsonERROR':
            packet = compose_packet(addr, CMD_RESPONSE_CODE[1][0], CMD_RESPONSE_CODE[1][1])
        else:
            packet = compose_packet(addr, CMD_RESPONSE_CODE[2][0], CMD_RESPONSE_CODE[2][1])
    except KeyError:
        packet = compose_packet(addr, CMD_RESPONSE_CODE[7][0], CMD_RESPONSE_CODE[7][1])
    return packet, command

async def simulator_server_handler(reader, writer):
    logger = logging.getLogger('SERVER_LOG')
    data = await reader.read(2048)
    message = data.decode()
    addr = writer.get_extra_info('peername')

    try:
        request = json.loads(message)
    except json.decoder.JSONDecodeError:
        request = {'command': 'jsonERROR'}

    packet, command = command_processor(addr, request)

    response = json.dumps(packet).encode('utf-8')
    writer.write(response)
    await writer.drain()

    logger.info('[%s_%s] Response: %s', addr, command, response)

    logger.info('Close the connection')
    writer.close()


async def simulator_server():
    local_server = await asyncio.start_server(simulator_server_handler, SIM_SERVER_HOST, SIM_SERVER_PORT)
    address = local_server.sockets[0].getsockname()
    logging.getLogger('SERVER_LOG').info('Serving on %s', address)

    async with local_server:
        await local_server.serve_forever()


async def simulator_client(sm):
    logger = logging.getLogger('SIM_CLIENT')
    while True:
        try:
            sm.simulate()

            rdr, wtr = await asyncio.open_connection(FE_SERVER_HOST, FE_SERVER_PORT)
            raw_comp_info = dict()
            for c_name, component in sm.components.items():
                raw_comp_info[c_name] = [component.ddp, component.res, component.cur]

            packet = {
                'command': 'loadData',
                'arguments': raw_comp_info
            }

            wtr.write(json.dumps(packet).encode())
            data = await rdr.read(100)
            logger.info('Response to %s', data.decode())
            wtr.close()

            await asyncio.sleep(1)
        except ConnectionRefusedError:
            logger.info('Connection Refused to %s:%d', FE_SERVER_HOST, FE_SERVER_PORT)


async def main(sm):
    define_simulator(sm)
    task1 = asyncio.create_task(simulator_client(sm))
    task2 = asyncio.create_task(simulator_server())
    await task1
    await task2

logging.basicConfig(level=logging.INFO)

loop = asyncio.get_event_loop()

try:
    loop.run_until_complete(main(SIM))
except KeyboardInterrupt:
    loop.stop()
