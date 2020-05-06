# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.
import json
import time
import os
import sys
import asyncio
from six.moves import input
import threading
# pylint: disable=import-error
from azure.iot.device.aio import IoTHubModuleClient
from azure.iot.device import Message
# pylint: enable=import-error

# Define the ALARM JSON message to send to IoT Hub.
TLM_MSG_TXT = '{{ "type": {type}, "pipe":, {pipe}, "sensor": {sensor}, "pipe_sensor": {pipe_sensor}, "flow": {flow}, "unit": {unit}, "timestamp": {timestamp} }}'
AL_MSG_TXT = '{{ "type": {type}, "pipe":, {pipe}, "zone": {sensor}, "pipe_zone": {pipe_zone}, "alarm": {alarm}, "timestamp": {timestamp} }}'

# global counters
TWIN_CALLBACKS = 0
RELATIVE_THRESHOLD = 0.3

SENSORS_IN_PIPES = [3, 3, 3, 3]
#SENSORS_IN_PIPES = [3, 3]

def initialize_controlList():
    global SENSORS_IN_PIPES
    controlList = []
    for i in range(len(SENSORS_IN_PIPES)):
        [controlList.append('pipe{}-sensor{}'.format(i+1, j+1))for j in range(SENSORS_IN_PIPES[i])]
    return controlList


def initialize_dataList():
    global SENSORS_IN_PIPES
    dataList = []
    for i in range(len(SENSORS_IN_PIPES)):
        dataList.append([0]*(SENSORS_IN_PIPES[i]))
    return dataList


# Func to determine if there is a leak
def detect_leak(dataList):
    leaks = []
    codes = []
    for i in range(len(SENSORS_IN_PIPES)):
        diffs = list(zip(dataList[i][:-1], dataList[i][1:]))
        for j, (x,y) in enumerate(diffs):
            difference = abs(y-x)
            print(f"Flow difference of {difference}")
            if difference != 0:
                leaks.append('pipe{}-sensor{}>sensor{}'.format(i+1, j+1, j+2))
                if difference >= RELATIVE_THRESHOLD*x:
                    codes.append(2)
                else:
                    codes.append(1)
        #[leaks.append('pipe{}-sensor{}>sensor{}'.format(i+1, j+1, j+2)) for j, (x, y) in enumerate(diffs) if abs(y-x) >= THRESHOLD*x]
    return leaks, codes


def get_pipe_sensor_ids(id):
    aux = id.split('-')
    pipeId, sensorId = aux[0][-1:], aux[1][-1:]
    return aux[0], aux[1], int(pipeId), int(sensorId)

async def main():
    try:
        if not sys.version >= "3.5.3":
            raise Exception( "The sample requires python 3.5.3+. Current version of Python: %s" % sys.version )
        print ( "IoT Hub Client for Python" )

        # The client object is used to interact with your Azure IoT hub.
        module_client = IoTHubModuleClient.create_from_edge_environment()
        
        # connect the client.
        await module_client.connect()

        # Define behavior for receiving an input message on input1
        # Because this is a filter module, we forward this message to the "output1" queue.
        async def input1_listener(module_client):
            controlList = initialize_controlList()
            dataList = initialize_dataList()
            while True:
                try:
                    input_message = await module_client.receive_message_on_input("input1")  # blocking call
                    message = input_message.data
                    messageText = message.decode('utf-8')
                    print(f"Message text: {messageText}")
                    messageJSON = json.loads(messageText)
                    print(f"Message json: {messageJSON}")
                    
                    pipe, sensor, pipeId, sensorId = get_pipe_sensor_ids(messageJSON["id"])
                    dataList[pipeId-1][sensorId-1] = messageJSON["flow"]
                    print(f"Current sensor datalist: {dataList}")
                    try:
                        controlList.remove(messageJSON["id"])
                        print(f"Rest of sensors to receive from: {controlList}")
                    except:
                        print(f"Duplicated measure for {messageJSON['id']}")

                    outMsgData = {}
                    outMsgData["type"], outMsgData["pipe"], outMsgData["sensor"], outMsgData["pipe_sensor"], outMsgData["flow"], outMsgData["unit"], outMsgData["timestamp"] = "telemetry", pipe, sensor, messageJSON["id"], messageJSON["flow"], messageJSON["unit"], messageJSON["timestamp"]
                    outMsgJSON = json.dumps(outMsgData)
                    
                    #msgFormatted = TLM_MSG_TXT.format(pipe=pipe, sensor=sensor, pipe_sensor=messageJSON["id"], flow=messageJSON["flow"], unit=messageJSON["unit"], timestamp=messageJSON["timestamp"])
                    outMsg = Message(outMsgJSON)
                    print(outMsg.data)

                    # Send Telemetry message to IoTHub
                    await module_client.send_message_to_output(outMsg, "output2")
                    print('Telemetry sent to IoTHub')

                    if not controlList:
                        print("Collected telemetry from all sensors")
                        leaks, codes = detect_leak(dataList)
                        print(f"Leaks detected: {leaks}")
                        # Reset control list
                        controlList = initialize_controlList()

                        for i, leak in enumerate(leaks):
                            leak_loc = leak.split("-")
                            print(leak_loc)
                            alMsgData = {}
                            alMsgData["type"], alMsgData["pipe"], alMsgData["zone"], alMsgData["pipe_zone"], alMsgData["alarm"], alMsgData["timestamp"] = "alarm", leak_loc[0], leak_loc[1], leak, codes[i], messageJSON["timestamp"]
                            alMsgJSON = json.dumps(alMsgData)
                            print(alMsgJSON)
                            alMsg = Message(alMsgJSON)
                            await module_client.send_message_to_output(alMsg, "output1")
                            await module_client.send_message_to_output(alMsg, "output2")
                            print('Sent alarm message to IoTHub to sensors')

                except Exception as ex:
                    print ( "Unexpected error in input1_listener: %s" % ex )

        # define behavior for halting the application
        def stdin_listener():
            while True:
                try:
                    selection = input("Press Q to quit\n")
                    if selection == "Q" or selection == "q":
                        print("Quitting...")
                        break
                except:
                    time.sleep(10)
                    
        # twin_patch_listener is invoked when the module twin's desired properties are updated.
        async def twin_patch_listener(module_client):
            global TWIN_CALLBACKS
            global RELATIVE_THRESHOLD
            while True:
                try:
                    data = await module_client.receive_twin_desired_properties_patch()  # blocking call
                    print( "The data in the desired properties patch was: %s" % data)
                    if "Threshold" in data:
                        RELATIVE_THRESHOLD = data["Threshold"]
                    TWIN_CALLBACKS += 1
                    print ( "Total calls confirmed: %d\n" % TWIN_CALLBACKS )
                except Exception as ex:
                    print ( "Unexpected error in twin_patch_listener: %s" % ex )

        # Schedule task for C2D Listener
        listeners = asyncio.gather(input1_listener(module_client), twin_patch_listener(module_client))

        print ( "The sample is now waiting for messages. ")

        # Run the stdin listener in the event loop
        loop = asyncio.get_event_loop()
        user_finished = loop.run_in_executor(None, stdin_listener)

        # Wait for user to indicate they are done listening for messages
        await user_finished

        # Cancel listening
        listeners.cancel()

        # Finally, disconnect
        await module_client.disconnect()

    except Exception as e:
        print ( "Unexpected error %s " % e )
        raise

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()

    # If using Python 3.7 or above, you can use following code instead:
    # asyncio.run(main())