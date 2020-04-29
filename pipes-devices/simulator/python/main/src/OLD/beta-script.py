"""Teoria de circuitos."""
import uuid
import numpy as np
import logging
from string import Template

LOGGER = logging.getLogger()
TYPE_ERROR_STR = Template('Only allowed $value of type $type')

NET_LIST = set()
REF = None

class Element:
    """Element class."""

    def __init__(self):
        """Initialize Base Properties."""
        self._ddp = float('inf')
        self._res = float('inf')
        self._cur = float('inf')
        self._one = uuid.uuid4()
        self._two = uuid.uuid4()

    @property
    def one(self):
        """Object connected in Pin 1."""
        return self._one

    @property
    def two(self):
        """Object connected in Pin 2."""
        return self._two

    @property
    def ddp(self):
        """Property of ddp."""
        return self._ddp

    @ddp.setter
    def ddp(self, val):
        if not isinstance(val, float):
            raise TypeError(TYPE_ERROR_STR.substitute(value='val', type='float'))
        self._ddp = val

    @property
    def res(self):
        """Property of res."""
        return self._res

    @res.setter
    def res(self, val):
        if not isinstance(val, float):
            raise TypeError(TYPE_ERROR_STR.substitute(value='val', type='float'))
        self._res = val

    @property
    def cur(self):
        """Property of cur."""
        return self._cur

    @cur.setter
    def cur(self, val):
        if not isinstance(val, float):
            raise TypeError(TYPE_ERROR_STR.substitute(value='val', type='float'))
        self._cur = val

class PowerSrc(Element):
    """Power Generator Element."""

    def __init__(self, **kwargs):
        """Initialize PowerSrc Properties."""
        super().__init__()
        self._ddp = kwargs.pop('ddp', float('inf'))

class Transducers(Element):
    """Transducers Element."""

    def __init__(self, **kwargs):
        """Initialize Transducers Properties."""
        super().__init__()
        self._res = kwargs.pop('res', float('inf'))

class FlowSrc(Element):
    """Flow Generator Element."""

    def __init__(self, **kwargs):
        """Initialize FlowSrc Properties."""
        super().__init__()
        self._cur = kwargs.pop('cur', float('inf'))


def connect(node_l, node_r):
    """Connect Elements."""
    global NET_LIST
    if not isinstance(node_r, uuid.UUID):
        LOGGER.debug(type(node_l))
        raise TypeError(TYPE_ERROR_STR.safe_substitute(value='node_r', type='uuid.UUID'))

    if not isinstance(node_l, uuid.UUID):
        LOGGER.debug(type(node_l))
        raise TypeError(TYPE_ERROR_STR.safe_substitute(value='node_l', type='uuid.UUID'))

    if node_l != node_r and (node_r, node_l) not in NET_LIST:
        NET_LIST.add((node_l, node_r))

def find_component(pin, loc):
    """Return a found component."""
    for k, v in  loc.items():
        if pin == v.one or pin == v.two:
            return v
    return None

def find_node(pin, lon):
    """Return node index in lon."""
    for index, el in  enumerate(lon):
        if pin in el:
            return index
    return None

def simulate(input_components):
    """Simulate the components properly connected."""
    global NET_LIST, LOGGER
    NODE_LIST = list()
    for net in NET_LIST:
        if len(NODE_LIST) == 0:
            NODE_LIST.append([net[0], net[1]])
        else:
            found = False
            for el in NODE_LIST:
                if net[0] in el:
                    el.append(net[1])
                    found = True
                    break
                elif net[1] in el:
                    el.append(net[0])
                    found = True
                    break
            if not found:
                NODE_LIST.append([net[0], net[1]])

    for index, node in enumerate(NODE_LIST):
        LOGGER.debug(f'NODE{index}: {node}')

    NODE_CHECKED = []
    NODE_NOT_CHECKED = [0]
    COMP_LIST = []
    while len(NODE_CHECKED) != len(NODE_LIST):
        update_node_list = NODE_NOT_CHECKED.copy()
        for el in update_node_list:
            for pin in NODE_LIST[el]:
                target_component = find_component(pin, input_components)
                node_one = find_node(target_component.one, NODE_LIST)
                node_two = find_node(target_component.two, NODE_LIST)
                target_node = node_one if node_one != el else node_two
                if target_node not in NODE_CHECKED:
                    COMP_LIST.append([el, target_node, target_component])
                    if target_node not in NODE_NOT_CHECKED:
                        NODE_NOT_CHECKED.append(target_node)
            if el not in NODE_CHECKED:
                NODE_CHECKED.append(el)
            NODE_NOT_CHECKED.remove(el)

    for index, net in enumerate(COMP_LIST):
        LOGGER.debug(f'C_NET{index}: {net}')


    NODE_REF = [ index for index, node in enumerate(NODE_LIST) if REF in node ][0]
    LOGGER.debug(f'NODE_REF: {NODE_REF}')
    KNOWN_NETS = [net for net in COMP_LIST if NODE_REF in net and isinstance(net[2], PowerSrc)]
    LOGGER.debug(f'KNOWN_NETS: {KNOWN_NETS}')

    KNOWN_NODES = list()
    for net in KNOWN_NETS:
        if net[0] not in KNOWN_NODES:
            KNOWN_NODES.append(net[0])
        if net[1] not in KNOWN_NODES:
            KNOWN_NODES.append(net[1])
    LOGGER.debug(f'KNOWN_NODES: {KNOWN_NODES}')

    UNKNOWN_NODES = [index for index, node in enumerate(NODE_LIST) if index not in KNOWN_NODES]
    LOGGER.debug(f'UNKNOWN_NODES: {UNKNOWN_NODES}')

    UNKNOWN_EQS = list()
    for node in UNKNOWN_NODES:
        result = 0.0
        coeficients = list()

        # Por cada pin en el nodo:
        for pin in NODE_LIST[node]:
            LOGGER.debug(f'Checking NODE{node}: PIN={pin}')
            # Busqueda de nodo extremo
            target_component = find_component(pin, input_components)
            LOGGER.debug(f'\t Component: {target_component}')
            target_net = [net for net in COMP_LIST if target_component in net][0]
            LOGGER.debug(f'\t NET: C_NET{target_net}')
            extreme_node = target_net[1] if target_net[0] == node else target_net[0]
            LOGGER.debug(f'\t Extreme node: NONE{extreme_node}')

            if isinstance(target_component, Transducers):
                LOGGER.debug(f'\t Component type: Transducers')
                # Flujo de nodo target: se calcula coeficiente_target*(-1 si tipo_1 else 1) y añade coeficiente_target al grupo_r
                coeficients.append((node, 1.0/target_component.res))

                # si nodo_extremo es conocido:
                if extreme_node in KNOWN_NODES:
                    if extreme_node != NODE_REF:
                        extreme_net = [net for net in KNOWN_NETS if net[1] == extreme_node or net[0] == extreme_node][0]
                        LOGGER.debug(f'\t Extreme net: NET{extreme_net}')
                        extreme_value = extreme_net[2].ddp if extreme_net[2].one in NODE_LIST[extreme_node] else -extreme_net[2].ddp
                        LOGGER.debug(f'\t Extreme value: {extreme_value}')
                        result += extreme_value/target_component.res
                else:
                    extreme_ceof = -1.0/target_component.res
                    coeficients.append((extreme_node, extreme_ceof))

            if isinstance(target_component, FlowSrc):
                LOGGER.debug(f'\t Component type: FlowSrc')
                # Flujo de nodo target: se calcula coeficiente_target*(-1 si tipo_1 else 1) y añade coeficiente_target al grupo_
                result += target_component.cur if pin == target_component.one else -target_component.cur
                #LOGGER.debug(f'\t Extreme value: NET{extreme_ceof}')
            LOGGER.debug(f'\t Result vector: {result}')
            LOGGER.debug(f'\t input_components vector: {coeficients}')

        full_coefs = list(range(len(UNKNOWN_NODES)))
        for index, node in enumerate(UNKNOWN_NODES):
            res_coef = 0.0
            for coef in coeficients:
                if coef[0] == node:
                    res_coef += coef[1]
            full_coefs[index] = res_coef
        UNKNOWN_EQS.append((result, full_coefs.copy()))
        LOGGER.debug(f'\t EQ vector: {UNKNOWN_EQS}')

    LOGGER.debug(f'UNKNOWN_EQS: {UNKNOWN_EQS}')

    UNKNOWN_S = np.array([el[0] for el in UNKNOWN_EQS])
    UNKNOWN_C = np.array([el[1] for el in UNKNOWN_EQS])
    SOLTUTION = list(np.linalg.solve(UNKNOWN_C, UNKNOWN_S))

    LOGGER.debug(f'NODE SOLUTION: {SOLTUTION}')

    NODE_POWER_VALUES = list(range(len(NODE_LIST)))
    NODE_POWER_VALUES[NODE_REF] = 0.0
    for index, node in enumerate(UNKNOWN_NODES):
        NODE_POWER_VALUES[node] = SOLTUTION[index]

    LOGGER.debug(f'POWER SOLUTIONS: {NODE_POWER_VALUES}')

    for index, net in enumerate(KNOWN_NETS):
        node = net[1] if NODE_REF == net[0] else net[0]
        value = net[2].ddp if net[2].one in NODE_LIST[node] else -net[2].ddp
        NODE_POWER_VALUES[node] = value
    LOGGER.debug(f'POWER SOLUTIONS: {NODE_POWER_VALUES}')

    SIM_NET_LIST = list()
    for net in COMP_LIST:
        net_order = 1.0 if net[2].one in NODE_LIST[net[0]] else -1.0
        net_ddp = ( NODE_POWER_VALUES[net[0]] - NODE_POWER_VALUES[net[1]] )*net_order

        if isinstance(net[2], Transducers):
            net_cur = net_ddp / net[2].res
            net_res = net[2].res
            net[2].ddp = net_ddp
            net[2].cur = net_cur
        elif isinstance(net[2], FlowSrc):
            net_cur = net[2].cur
            net_res = float('inf')
            net[2].ddp = net_ddp
            net[2].res = float('inf')
        else:
            net_cur = None
            net_res = 0.0
            net[2].res = 0.0

        SIM_NET_LIST.append([net[0],
                             net[1],
                             net_ddp,
                             net_cur,
                             net_res,
                             net[2]
                             ])

    for sim_net in SIM_NET_LIST:
        if sim_net[3] is None:
            cur_check_node = sim_net[0] if sim_net[0] != NODE_REF else sim_net[1]
            calc_cur = 0.0
            for pin in NODE_LIST[cur_check_node]:
                check_component = find_component(pin, input_components)
                if not isinstance(check_component, PowerSrc):
                    comp_cur = [search_net[3] for search_net in SIM_NET_LIST if check_component == search_net[5]][0]
                    calc_cur += comp_cur if check_component.two in NODE_LIST[cur_check_node] else -comp_cur
            sim_net[3] = calc_cur
            sim_net[-1].cur = calc_cur

    for index, net in enumerate(SIM_NET_LIST):
        LOGGER.debug(f'SIM_NET_LIST_{index}: {net}')

    headers = ['Components', ' Power ', 'Flow', 'Transmitance']
    LOGGER.info('-'*55)
    LOGGER.info('| {0:^10} | {1:^10} | {2:^10} | {3:^12} |'.format(*headers))
    LOGGER.info('-'*55)
    for key, comp in input_components.items():
        LOGGER.info(f'| {key:<10} | {comp.ddp:>10.5f} | {comp.cur:>10.5f} | {comp.res:>12.5f} |')
    LOGGER.info('-'*55)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    MyComps = {
        'V_ONE': PowerSrc(ddp=2),
        'V_TWO': PowerSrc(ddp=1),
        'I_ONE': FlowSrc(cur=1),
        'R_ONE': Transducers(res=1),
        'R_TWO': Transducers(res=1),
        'R_THREE': Transducers(res=1),
        'R_FOUR': Transducers(res=1),
        'R_FIVE': Transducers(res=1),
        'R_SIX': Transducers(res=1),
        'R_SEVEN': Transducers(res=1),
        'R_EIGHT': Transducers(res=1)
        }

    connect(MyComps['V_ONE'].one, MyComps['R_ONE'].one)
    connect(MyComps['V_ONE'].one, MyComps['R_TWO'].one)
    connect(MyComps['R_ONE'].two, MyComps['R_THREE'].one)
    connect(MyComps['R_TWO'].two, MyComps['R_THREE'].two)
    connect(MyComps['R_THREE'].two, MyComps['R_FOUR'].one)
    connect(MyComps['R_FOUR'].two, MyComps['V_ONE'].two)
    connect(MyComps['R_ONE'].two, MyComps['R_SIX'].one)
    connect(MyComps['R_ONE'].two, MyComps['R_FIVE'].one)
    connect(MyComps['R_FIVE'].two, MyComps['I_ONE'].one)
    connect(MyComps['I_ONE'].two, MyComps['V_ONE'].two)
    connect(MyComps['R_SIX'].two, MyComps['R_SEVEN'].one)
    connect(MyComps['R_SIX'].two, MyComps['R_EIGHT'].one)
    connect(MyComps['R_SEVEN'].two, MyComps['V_ONE'].two)
    connect(MyComps['R_EIGHT'].two, MyComps['V_TWO'].one)
    connect(MyComps['V_TWO'].two, MyComps['V_ONE'].two)

    REF = MyComps['V_ONE'].two
    simulate(MyComps)

    LOGGER.info(NET_LIST)
