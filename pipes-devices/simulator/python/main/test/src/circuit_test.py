"""
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@                              @@@@@,@@@@@@@@@@@%/%@@@@@@@@@@@,@@@@@@@&&@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@      PIPE DEMO SYSTEM        @                                   @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
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
@@@@@@@@@@@@@@@@@@@@@@@ @@@@@@@@@@@              [WATER_IN_1]----(1_S1)-----(1_S2)-----(1_S3)--|  @@
@@@@@@@@@@@@@@@@@@@@@@*  @@@@@@@@@@                                                            |  @@
@@@@@@@@@@@@@@@@@@@@@     @@@@@@@@@                           |--(1_S6)-----(1_S5)-----(1_S4)--|  @@
@@@@@@@@@@@@@@@@&@@         @@@@@@@                           |                                   @@
@@@@@@@@@@@@@@@@@.            @@@@@                +--(2_S1)--+--(4_S1)--+                        @@
@@@@@@@@@@@@@@@@@           @  @@@@                |          |          |                        @@
@@@@@@@@@@@@@@@@@           @ ,@@@@              (2_S2)     (3_S1)     (4_S2)                     @@
@@@@@@@@@@@@@@@@@@        /// @@@@@                |          |          |        =()=            @@
@@@@@@@@@@@@@@@@@@@@   ,/( @@@@@@@@    =()=        |          |          |____,/'\_||_            @@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@    _||_/'\,____|          |    TAP_3 |____( (___  `.          @@
@@@@@@@@@@@@@@@@@@@@@@@ @@@@@@@@@@@  .´  ___) )____| TAP_1    |               `\./  `=='          @@
@@@@@@@@@@@@@@@@@@@@@@*  @@@@@@@@@@  '==´  \./´               |                      ||           @@
@@@@@@@@@@@@@@@@@@@@@     @@@@@@@@@   ||          =()=      (3_S2)                   ||           @@
@@@@@@@@@@@@@@@@&@@         @@@@@@@   ||          _||_/'\,____|                      ||           @@
@@@@@@@@@@@@@@@@@.            @@@@@   ||        .´  ___) )____| TAP_2                ||           @@
@@@@@@@@@@@@@@@@@           @  @@@@   ||        '==´  \./´                           ||           @@
@@@@@@@@@@@@@@@@@           @ ,@@@@   ||         ||                                  ||           @@
@@@@@@@@@@@@@@@@@@        /// @@@@@   ||         ||                                  ||           @@
@@@@@@@@@@@@@@@@@@@@   ,/( @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
----------------------------------------------------------------------------------------------------
"""
import logging
import circuit

logging.basicConfig(level=logging.INFO)
SM = circuit.Simulator()

SM.register_component('WATER_IN_1', circuit.PowerSrc(ddp=100))
SM.register_component('PIPE_1_S1', circuit.Transducers(res=1))
SM.register_component('PIPE_1_S2', circuit.Transducers(res=1))
SM.register_component('PIPE_1_S3', circuit.Transducers(res=1))
SM.register_component('PIPE_1_S4', circuit.Transducers(res=1))
SM.register_component('PIPE_1_S5', circuit.Transducers(res=1))
SM.register_component('PIPE_1_S6', circuit.Transducers(res=1))
SM.register_component('PIPE_2_S1', circuit.Transducers(res=1))
SM.register_component('PIPE_4_S1', circuit.Transducers(res=1))
SM.register_component('PIPE_3_S1', circuit.Transducers(res=1))
SM.register_component('PIPE_3_S2', circuit.Transducers(res=1))
SM.register_component('PIPE_4_S2', circuit.Transducers(res=1))
SM.register_component('PIPE_2_S2', circuit.Transducers(res=1))
SM.register_component('TAP_1', circuit.Transducers(res=1))
SM.register_component('TAP_2', circuit.Transducers(res=1))
SM.register_component('TAP_3', circuit.Transducers(res=1))

SM.connect(SM.get_component('WATER_IN_1').one, SM.get_component('PIPE_1_S1').one)
SM.connect(SM.get_component('PIPE_1_S1').two, SM.get_component('PIPE_1_S2').one)
SM.connect(SM.get_component('PIPE_1_S2').two, SM.get_component('PIPE_1_S3').one)
SM.connect(SM.get_component('PIPE_1_S3').two, SM.get_component('PIPE_1_S4').one)
SM.connect(SM.get_component('PIPE_1_S4').two, SM.get_component('PIPE_1_S5').one)
SM.connect(SM.get_component('PIPE_1_S5').two, SM.get_component('PIPE_1_S6').one)
SM.connect(SM.get_component('PIPE_1_S6').two, SM.get_component('PIPE_2_S1').one)
SM.connect(SM.get_component('PIPE_2_S1').two, SM.get_component('PIPE_2_S2').one)
SM.connect(SM.get_component('PIPE_2_S2').two, SM.get_component('TAP_1').one)
SM.connect(SM.get_component('TAP_1').two, SM.get_component('WATER_IN_1').two)
SM.connect(SM.get_component('PIPE_1_S6').two, SM.get_component('PIPE_3_S1').one)
SM.connect(SM.get_component('PIPE_3_S1').two, SM.get_component('PIPE_3_S2').one)
SM.connect(SM.get_component('PIPE_3_S2').two, SM.get_component('TAP_2').one)
SM.connect(SM.get_component('TAP_2').two, SM.get_component('WATER_IN_1').two)
SM.connect(SM.get_component('PIPE_1_S6').two, SM.get_component('PIPE_4_S1').one)
SM.connect(SM.get_component('PIPE_4_S1').two, SM.get_component('PIPE_4_S2').one)
SM.connect(SM.get_component('PIPE_4_S2').two, SM.get_component('TAP_3').one)
SM.connect(SM.get_component('TAP_3').two, SM.get_component('WATER_IN_1').two)

SM.reference = SM.get_component('WATER_IN_1').two

SM.simulate()
