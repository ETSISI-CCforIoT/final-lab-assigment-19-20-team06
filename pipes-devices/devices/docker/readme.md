# Flowmeters docker images

## Brief description

All devices has a config.json file for configuration with the next structure:

    {
        "parameter_name": parameter_value,
        ...
    }

The configuration can be applied using environ variables.

Environ variables and config.json variable has the same name for the same value to configure.  The available  parameters
are:

###### Table 1. Flowmeter parameters

| Parameter                 | Value Type | Description                      |
|:------------------------- |:----------:|:-------------------------------- |
| **mqtt\_broker\_ip**      |     string | MQTT Broker IP                   |
| **mqtt\_broker\_port**    |    integer | MQTT Broker Port                 |
| **mqtt\_broker\_topic**   |     string | MQTT topic for send/receive data |
| **sim\_frontend\_ip**     |     string | Simulator Frontend IP            |
| **sim\_frontend\_port**   |    integer | Simulator Frontend Port          |
| **flowmeter\_sim\_id**    |     string | Flowmeter Simulator ID           |
| **flowmeter\_cloud\_id**  |     string | Flowmeter Cloud ID               |

The docker folder contains a example config.json file. This file can be modified.  All the parameters in config file are 
optional:

    {
        "mqtt_broker_ip": "40.68.175.17",
        "mqtt_broker_port": 1883,
        "mqtt_broker_topic": "/floors/floor1/data",
        "sim_frontend_ip": "192.168.187.133", 
        "sim_frontend_port": 8888,
        "flowmeter_sim_id": "PIPE_1_S1",
        "flowmeter_cloud_id": "pipe1-sensor1"
    }

By default, the parameters not defined by config.json or environ variables are:

###### Table 2. Default values of flowmeter parameters 

| Parameter                 |            Default Value |
|:------------------------- | ------------------------:|
| **mqtt\_broker\_ip**      |            _'127.0.0.1'_ |
| **mqtt\_broker\_port**    |                   _1883_ |
| **mqtt\_broker\_topic**   | _'floors\/floor1\/data'_ |
| **sim\_frontend\_ip**     |            _'127.0.0.1'_ |
| **sim\_frontend\_port**   |                   _8888_ |
| **flowmeter\_sim\_id**    |          _'PIPE\_1\_S1'_ |
| **flowmeter\_cloud\_id**  |        _'pipe1-sensor1'_ |

## How to use it

### Docker image creation

To create the docker image just run the next command into the folder with the Dockerfile:

    sudo docker build --tag image_tag:0.0 .

Where **image\_tag** is the name of your image and **0.0** is your image tag version (1.4, 5.6, ...)

### Docker image run in a new container

To run the previous created docker image just run the next command:

    sudo docker run --name container_pretty_name image_tag:0.0

Where **image\_tag** is the name of your image and **0.0** is your image tag version (1.4, 5.6, ...) and the 
container\_pretty\_name is a human readable name to use for operate with the container.

Further information of docker usage [here](https://docs.docker.com/get-started/). 

### Customized docker devices with environ variable

You can customize the behavior of the flowmeter device passing to the docker container the environment variables shown 
in [table 2](#table-2.-default-values-of-flowmeter-parameters) as it is shown in the next command.  

    sudo docker run -e flowmeter_sim_id=PIPE_1_S1 -e flowmeter_cloud_id=pipe1-sensor1 image_tag:0.0