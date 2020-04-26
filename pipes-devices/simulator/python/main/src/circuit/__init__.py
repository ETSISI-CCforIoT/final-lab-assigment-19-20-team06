"""Teoria de circuitos."""
import uuid
import logging
from string import Template
import numpy as np

TYPE_ERROR_STR = Template('Only allowed $value of type $type')

def _find_node(pin, lon):
    """Return node index in lon."""
    for index, node in  enumerate(lon):
        if pin in node:
            return index
    return None

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

class Simulator:
    """Engine to process conservative energy circuits.
       Could be registered Potential Sources, Transducers and Flow Maintainers or Flow Sources.

       All components registered must be fully connected between them.
    """

    def __init__(self):
        """Initialize values."""
        self._net_list = set()
        self.__node_list = list()
        self.__known_nodes = list()
        self.__unknown_nodes = list()
        self.__reference_node = 0
        self.__ref = None
        self._components = dict()
        self.logger = logging.getLogger()

    @property
    def reference(self):
        """Reference pin."""
        return self.__ref

    @reference.setter
    def reference(self, pin):
        """Reference pin."""
        if not isinstance(pin, uuid.UUID):
            raise TypeError(TYPE_ERROR_STR.substitute(value='pin', type='uuid.UUID'))

        pin_found = False
        for net in self._net_list:
            if pin in net:
                pin_found = True

        if not pin_found:
            raise AttributeError('Component pin not found to assign as reference point.')
        self.__ref = pin

    def _initialize_vectors(self):
        """Init simulation vectors for a new simulation cycle."""
        self.__node_list = list()
        self.__known_nodes = list()
        self.__unknown_nodes = list()
        self.__reference_node = 0
        self.logger.debug('Variables Initialized!')
        self.logger.debug('\t %s %s %s %s', 
                          self.__node_list,
                          self.__known_nodes,
                          self.__unknown_nodes,
                          self.__reference_node)

    def _find_component(self, pin):
        """Return a found component."""
        for component in self._components.values():
            if pin in (component.one, component.two):
                return component
        return None

    def _generate_node_list(self):
        """Create the list of nodes."""
        for net in self._net_list:
            if len(self.__node_list) == 0:
                self.__node_list.append([net[0], net[1]])
            else:
                found = False
                for node in self.__node_list:
                    if net[0] in node:
                        node.append(net[1])
                        found = True
                        break
                    if net[1] in node:
                        node.append(net[0])
                        found = True
                        break
                if not found:
                    self.__node_list.append([net[0], net[1]])

        for index, node in enumerate(self.__node_list):
            self.logger.debug('NODE%s: %s', index, node)

    #TODO Locate only connected components (Not components on air)
    def _generate_pre_sim_net_list(self):
        """NODE ALGORITHM STEP 1: Locate nets
            Check all nodes and generate the components and node net list.
        """
        comp_net_list = list()
        node_checked = list()
        node_not_checked = [0]
        while len(node_checked) != len(self.__node_list):
            update_node_list = node_not_checked.copy()
            for node in update_node_list:
                for pin in self.__node_list[node]:
                    target_comp = self._find_component(pin)
                    node_one = _find_node(target_comp.one, self.__node_list)
                    node_two = _find_node(target_comp.two, self.__node_list)
                    target_node = node_one if node_one != node else node_two
                    if target_node not in node_checked:
                        comp_net_list.append([node, target_node, target_comp])
                        if target_node not in node_not_checked:
                            node_not_checked.append(target_node)
                if node not in node_checked:
                    node_checked.append(node)
                node_not_checked.remove(node)

        for index, net in enumerate(comp_net_list):
            self.logger.debug('COMP_NET%s: %s', index, net)

        return comp_net_list

    def _get_reference_node(self):
        """NODE ALGORITHM STEP 2: Select a reference node
            Extract reference node from list of nodes.
        """
        if self.__ref is None:
            max_len = max([len(node) for node in self.__node_list])
            self.__reference_node = [index for index, node in enumerate(self.__node_list)
                                     if max_len == len(node)][0]
        else:
            self.__reference_node = [index for index, node in enumerate(self.__node_list)
                                     if self.__ref in node][0]
            self.logger.info('REFERENCE NODE %s %s',
                             'EVALUATED' if self.__ref is None else 'FORCED',
                             self.__reference_node)

    def _get_known_nets(self, comp_net_list):
        """NODE ALGORITHM STEP 3.1: Extract the node algoritm known nets.
            A known net is the net associated to a PowerSrc component.
        """
        known_nets = [net for net in comp_net_list
                      if self.__reference_node in net and isinstance(net[2], PowerSrc)]
        self.logger.debug('KNOWN NETS: %s', known_nets)
        return known_nets

    def _get_known_nodes(self, known_nets):
        """NODE ALGORITHM STEP 3.2: Extract the node algoritm known nodes.
           Identify the known nodes of the node algoritm.
        """
        for net in known_nets:
            if net[0] not in self.__known_nodes:
                self.__known_nodes.append(net[0])
            if net[1] not in self.__known_nodes:
                self.__known_nodes.append(net[1])
        self.logger.debug('KNOWN NODES: %s', self.__known_nodes)

    def _get_unknown_nodes(self):
        """NODE  ALGORITHM  STEP 4:  Conform  the  vector of u nknown  nodes to  look for  the  node
           ecuations.

           Extract from the self.__node_list all the nodes not present in self.__known_nodes.
        """
        self.__unknown_nodes = [index for index, node in enumerate(self.__node_list)
                                if index not in self.__known_nodes]
        self.logger.debug('UNKNOWN NODES: %s', self.__unknown_nodes)

    def _find_target_net(self, comp_net_list, target_component):
        """Find information of the node unknown to check."""
        target_net = [net for net in comp_net_list if target_component in net][0]
        self.logger.debug('\t COMPONENT NET: C_NET%s', target_net)

        return target_net

    def _extreme_known_value(self, known_nets, extreme_node):
        """Calculate a node coeficient pair."""
        extreme_net = [net for net in known_nets if extreme_node in (net[0], net[1])][0]
        self.logger.debug('\t EXTREME NET: %s', extreme_net)
        value_sign = 1.0 if extreme_net[2].one in self.__node_list[extreme_node] else -1.0
        extreme_value = extreme_net[2].ddp*value_sign
        self.logger.debug('\t EXTREME POWER VALUE: %s', extreme_value)
        return extreme_value

    def _nodes_checker(self, node, known_nets, comp_net_list):
        result = 0.0
        coeficients = list()
        for pin in self.__node_list[node]:
            self.logger.debug('-- CHECKING NODE%s: PIN=%s --', node, pin)
            # Busqueda de nodo extremo
            target_comp = self._find_component(pin)
            self.logger.debug('\t TARGET COMPONENT: %s', target_comp)
            target_net = self._find_target_net(comp_net_list, target_comp)

            extreme_node = target_net[1] if target_net[0] == node else target_net[0]
            self.logger.debug('\t EXTREME NODE: %s', extreme_node)

            if isinstance(target_comp, Transducers):
                self.logger.debug('\t COMPONENT TYPE: Transducers')
                coeficients.append((node, 1.0/target_comp.res))

                if extreme_node in self.__known_nodes:
                    if extreme_node != self.__reference_node:
                        raw_value = self._extreme_known_value(known_nets, extreme_node)
                        result += raw_value/target_comp.res
                else:
                    raw_value = -1.0/target_comp.res
                    coeficients.append((extreme_node, raw_value))

            if isinstance(target_comp, FlowSrc):
                self.logger.debug('\t COMPONENT TYPE: FlowSrc')
                result += target_comp.cur if pin == target_comp.one else -target_comp.cur
            self.logger.debug('\t CONSTANT VALUE: %s', result)
            self.logger.debug('\t COEFICIENTS VALUES: %s', coeficients)

        return result, coeficients

    def _analize_node(self, node, known_nets, comp_net_list):
        result, coeficients = self._nodes_checker(node, known_nets, comp_net_list)

        full_coefs = list(range(len(self.__unknown_nodes)))
        for index, u_node in enumerate(self.__unknown_nodes):
            res_coef = 0.0
            for coef in coeficients:
                if coef[0] == u_node:
                    res_coef += coef[1]
            full_coefs[index] = res_coef
        return (result, full_coefs.copy())

    def _linear_solve_equations(self, equation_matrix):
        """Solve linear matrix."""
        contants_vector = np.array([el[0] for el in equation_matrix])
        coeficients_vector = np.array([el[1] for el in equation_matrix])

        solutions_vector = None
        attempts = 10#MAX_ATTEMPTS
        while attempts > 1:
            try:
                solutions_vector = list(np.linalg.solve(coeficients_vector, contants_vector))
                attempts = 0
            except np.linalg.LinAlgError as exception:
                attempts -= 1
                if attempts == 1:
                    self.logger.error(exception)

        self.logger.debug('MATRIX SOLUTIONS: %s', solutions_vector)
        return solutions_vector

    def _solve_linear_unknown_powers(self, node_powers_vector, known_nets, comp_net_list):
        unknown_equation_matrix = list()
        for node in self.__unknown_nodes:
            # Por cada pin en el nodo:
            node_equation = self._analize_node(node, known_nets, comp_net_list)
            unknown_equation_matrix.append(node_equation)
            self.logger.debug('\t MATRIX UPDATE: %s', unknown_equation_matrix)
        self.logger.debug('FINAL MATRIX: %s', unknown_equation_matrix)
        unknown_solutions = self._linear_solve_equations(unknown_equation_matrix)

        for index, node in enumerate(self.__unknown_nodes):
            node_powers_vector[node] = unknown_solutions[index]

        self.logger.debug('POWER SOLUTIONS: %s', node_powers_vector)

    #TODO: Known Node Error
    def _solve_known_powers(self, node_powers_vector, known_nets):
        for net in known_nets:
            node = net[1] if self.__reference_node == net[0] else net[0]
            value = net[2].ddp if net[2].one in self.__node_list[node] else -net[2].ddp
            node_powers_vector[node] = value
        self.logger.debug('POWER SOLUTIONS: %s', node_powers_vector)

    def _update_component_values(self, comp_net_list, node_powers_vector):
        for net in comp_net_list:
            net_order = 1.0 if net[2].one in self.__node_list[net[0]] else -1.0
            net_ddp = (node_powers_vector[net[0]] - node_powers_vector[net[1]])*net_order

            if isinstance(net[2], Transducers):
                net[2].ddp = net_ddp
                net[2].cur = net_ddp / net[2].res
            elif isinstance(net[2], FlowSrc):
                net[2].ddp = net_ddp
                net[2].res = float('inf')
            else:
                net[2].res = 0.0

        for sim_net in comp_net_list:
            if isinstance(sim_net[2], PowerSrc):
                check_node = sim_net[0] if sim_net[0] != self.__reference_node else sim_net[1]
                calc_cur = 0.0
                for pin in self.__node_list[check_node]:
                    check_comp = self._find_component(pin)
                    if not isinstance(check_comp, PowerSrc):
                        comp_cur = [search_net[2].cur for search_net in comp_net_list
                                    if check_comp == search_net[2]][0]
                        cur_sign = 1.0 if check_comp.two in self.__node_list[check_node] else -1.0
                        calc_cur += comp_cur * cur_sign
                sim_net[2].cur = calc_cur

    def _check_net_list(self):
        """Check unconnected components in the list."""
        for c_name, c_comp in self._components.copy().items():
            found_pin_one = False
            for conn_tuple in self._net_list:
                if c_comp.one in conn_tuple:
                    found_pin_one = True

            found_pin_two = False
            for conn_tuple in self._net_list:
                if c_comp.two in conn_tuple:
                    found_pin_two = True

            if not found_pin_one and not found_pin_two:
                self._components.pop(c_name)
                self.logger.info('Removed unused component %s.', c_name)
            elif not found_pin_one:
                raise AttributeError(f'Component {c_name} pin one on the air.')
            elif not found_pin_two:
                raise AttributeError(f'Component {c_name} pin one on the air.')

    def connect(self, node_l, node_r):
        """Connect Elements."""
        if not isinstance(node_r, uuid.UUID):
            self.logger.debug(type(node_l))
            raise TypeError(TYPE_ERROR_STR.safe_substitute(value='node_r', type='uuid.UUID'))

        if not isinstance(node_l, uuid.UUID):
            self.logger.debug(type(node_l))
            raise TypeError(TYPE_ERROR_STR.safe_substitute(value='node_l', type='uuid.UUID'))

        if node_l != node_r and (node_r, node_l) not in self._net_list:
            self._net_list.add((node_l, node_r))

    def print_components_info(self):
        """Display information of the components to simulate."""
        headers = ['Components', ' Power ', 'Flow', 'Transmitance']
        self.logger.info('-'*55)
        self.logger.info('| {0:^10} | {1:^10} | {2:^10} | {3:^12} |'.format(*headers))
        self.logger.info('-'*55)
        for key, comp in self._components.items():
            str_out = f'| {key:<10} | {comp.ddp:>10.5f} | {comp.cur:>10.5f} | {comp.res:>12.5f} |'
            self.logger.info(str_out)
        self.logger.info('-'*55)

    def simulate(self):
        """Simulate the components properly connected."""
        if len(self._components) <= 2:
            raise AttributeError('Add some components to the list.')

        self._check_net_list()
        self._initialize_vectors()
        self._generate_node_list()
        comp_net_list = self._generate_pre_sim_net_list()
        self._get_reference_node()

        known_nets = self._get_known_nets(comp_net_list)
        self._get_known_nodes(known_nets)
        self._get_unknown_nodes()

        # Solve Unknown Nodes
        node_powers_vector = list(range(len(self.__node_list)))
        node_powers_vector[self.__reference_node] = 0.0
        if len(self.__unknown_nodes) > 0:
            self._solve_linear_unknown_powers(node_powers_vector, known_nets, comp_net_list)

        self._solve_known_powers(node_powers_vector, known_nets)

        self._update_component_values(comp_net_list, node_powers_vector)
        self.print_components_info()

    def register_component(self, name, component):
        """Add a component to the Simulator component list."""
        if not isinstance(name, str):
            raise TypeError(TYPE_ERROR_STR.substitute(value='name', type='str'))

        if not isinstance(component, Element):
            raise TypeError(TYPE_ERROR_STR.substitute(value='component', type='Element'))

        if name in self._components:
            raise AttributeError('Name component is already in the list. Names must be unique.')

        for c_name, c_el in self._components.items():
            if component == c_el:
                raise AttributeError('component is already in the list.')

        self._components[name] = component

    def deregister_component(self, name):
        """Remove a component from the Simulator component list.
            All the connections will be removed!
        """
        if not isinstance(name, str):
            raise TypeError(TYPE_ERROR_STR.substitute(value='name', type='str'))

        component_to_remove = self.get_component(name)

        for conn_tuple in self._net_list.copy():
            if component_to_remove.one in conn_tuple or component_to_remove.two in conn_tuple:
                self._net_list.remove(conn_tuple)

        return self._components.pop(name)

    def get_component(self, name):
        """Return the component Identify by the string name."""
        if not isinstance(name, str):
            raise TypeError(TYPE_ERROR_STR.substitute(value='name', type='str'))

        if name not in self._components:
            raise AttributeError('Component not found.')

        return self._components[name]

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    EXAMPLE_SIM = Simulator()

    EXAMPLE_SIM.register_component('V_ONE', PowerSrc(ddp=2))
    EXAMPLE_SIM.register_component('V_TWO', PowerSrc(ddp=1))
    EXAMPLE_SIM.register_component('I_ONE', FlowSrc(cur=1))
    EXAMPLE_SIM.register_component('R_ONE', Transducers(res=1))
    EXAMPLE_SIM.register_component('R_TWO', Transducers(res=1))
    EXAMPLE_SIM.register_component('R_THREE', Transducers(res=1))
    EXAMPLE_SIM.register_component('R_FOUR', Transducers(res=1))
    EXAMPLE_SIM.register_component('R_FIVE', Transducers(res=1))
    EXAMPLE_SIM.register_component('R_SIX', Transducers(res=1))
    EXAMPLE_SIM.register_component('R_SEVEN', Transducers(res=1))
    EXAMPLE_SIM.register_component('R_EIGHT', Transducers(res=1))

    EXAMPLE_SIM.connect(EXAMPLE_SIM.get_component('V_ONE').one,
                        EXAMPLE_SIM.get_component('R_ONE').one)
    EXAMPLE_SIM.connect(EXAMPLE_SIM.get_component('V_ONE').one,
                        EXAMPLE_SIM.get_component('R_TWO').one)
    EXAMPLE_SIM.connect(EXAMPLE_SIM.get_component('R_ONE').two,
                        EXAMPLE_SIM.get_component('R_THREE').one)
    EXAMPLE_SIM.connect(EXAMPLE_SIM.get_component('R_TWO').two,
                        EXAMPLE_SIM.get_component('R_THREE').two)
    EXAMPLE_SIM.connect(EXAMPLE_SIM.get_component('R_THREE').two,
                        EXAMPLE_SIM.get_component('R_FOUR').one)
    EXAMPLE_SIM.connect(EXAMPLE_SIM.get_component('R_FOUR').two,
                        EXAMPLE_SIM.get_component('V_ONE').two)
    EXAMPLE_SIM.connect(EXAMPLE_SIM.get_component('R_ONE').two,
                        EXAMPLE_SIM.get_component('R_SIX').one)
    EXAMPLE_SIM.connect(EXAMPLE_SIM.get_component('R_ONE').two,
                        EXAMPLE_SIM.get_component('R_FIVE').one)
    EXAMPLE_SIM.connect(EXAMPLE_SIM.get_component('R_FIVE').two,
                        EXAMPLE_SIM.get_component('I_ONE').one)
    EXAMPLE_SIM.connect(EXAMPLE_SIM.get_component('I_ONE').two,
                        EXAMPLE_SIM.get_component('V_ONE').two)
    EXAMPLE_SIM.connect(EXAMPLE_SIM.get_component('R_SIX').two,
                        EXAMPLE_SIM.get_component('R_SEVEN').one)
    EXAMPLE_SIM.connect(EXAMPLE_SIM.get_component('R_SIX').two,
                        EXAMPLE_SIM.get_component('R_EIGHT').one)
    EXAMPLE_SIM.connect(EXAMPLE_SIM.get_component('R_SEVEN').two,
                        EXAMPLE_SIM.get_component('V_ONE').two)
    EXAMPLE_SIM.connect(EXAMPLE_SIM.get_component('R_EIGHT').two,
                        EXAMPLE_SIM.get_component('V_TWO').one)
    EXAMPLE_SIM.connect(EXAMPLE_SIM.get_component('V_TWO').two,
                        EXAMPLE_SIM.get_component('V_ONE').two)

    #EXAMPLE_SIM.deregister_component('V_ONE')

    EXAMPLE_SIM.simulate()
	
# import paho.mqtt.client as paho
# import json

# broker="40.68.175.17"
# port=1883

# def on_publish(client,userdata,result):             #create function for callback
    # print("data published \n")
    # pass

# msg=dict()
# msg["pipe"]="pipe1"
# msg["sensor"]="sensor1"
# msg["pipe_sensor"]="pipe1-sensor1"
# msg["flow"]=1
# msg["unit"]="L/min"
# j_msg=json.dumps(msg)


# client1= paho.Client("control1")                         #create client object
# client1.on_publish = on_publish                          #assign function to callback
# client1.connect(broker,port)                             #establish connection
# ret= client1.publish("floors/floor1/data",j_msg)         #publish
