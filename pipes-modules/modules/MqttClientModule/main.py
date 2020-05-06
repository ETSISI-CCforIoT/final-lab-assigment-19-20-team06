# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.
import json
import time
import random
# pylint: disable=import-error
from azure.iot.device import IoTHubModuleClient, Message
import paho.mqtt.client as mqtt
# pylint: enable=import-error


# Mqtt client config variables
broker_address= "40.68.175.17"      #Broker address
port = 1883                         #Broker port
user = "group06"                    #Connection username
password = "CCgroup06"              #Connection password

# Define the JSON message to send to IoT Hub.
MSG_TXT = '{{ "id": {id}, "flow": {flow}, "unit": {unit}, "timestamp": {timestamp} }}'


def iothub_client_init():
    # Create an IoT Hub client
    client = IoTHubModuleClient.create_from_edge_environment()
    return client
    
def iothub_client_telemetry_sample_run():

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(clientMqtt, userdata, flags, rc):
        print("Connected to mqtt broker with result code "+str(rc))
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        clientMqtt.subscribe("/floors/floor1/data")

    # The callback for when a PUBLISH message is received from the server.
    def on_message(client, userdata, msg):
        # Build the message with MQTT telemetry values.
        message = msg.payload.decode("utf-8")
        print("Message received on mqtt client: \n" + message)
        # Send the message.
        print( "Sending message to processing module" )
        module_client.send_message_to_output(msg.payload, "output1")


    print ( "IoT Gateway forwarding messages, press Ctrl-C to exit" )
    # Azure client
    module_client = iothub_client_init()

    # Mqtt client
    clientMqtt = mqtt.Client()
    clientMqtt.on_connect = on_connect
    clientMqtt.on_message = on_message
    clientMqtt.connect(broker_address, port)
    clientMqtt.loop_start()  

    while True:
        try: 
            input_message = module_client.receive_message_on_input("input1")  # blocking call
            message = input_message.data
            messageText = message.decode('utf-8')
            print(f"Message text: {messageText}")
            # Send message to MQTT broker
            #publish.single("paho/test/single", "payload", hostname="iot.eclipse.org")
            clientMqtt.publish("/floors/floor1/alarms", message)
            time.sleep(1)
        except KeyboardInterrupt:
            print ( "Gateway stopped" )

if __name__ == '__main__':
    print ( "IoT Hub Quickstart #1 - Simulated device" )
    print ( "Press Ctrl-C to exit" )
    iothub_client_telemetry_sample_run()