#!/bin/bash

if [ `whoami` != 'root' ]; then
        echo Please run this script as root 
        exit
else 
        echo Running new containers
        docker run --detach -e flowmeter_sim_id=PIPE_1_S1 -e flowmeter_cloud_id=pipe1-sensor1 --name fw1 fw:1.4
        docker run --detach -e flowmeter_sim_id=PIPE_1_S2 -e flowmeter_cloud_id=pipe1-sensor2 --name fw2 fw:1.4
        docker run --detach -e flowmeter_sim_id=PIPE_1_S3 -e flowmeter_cloud_id=pipe1-sensor3 --name fw3 fw:1.4
        docker run --detach -e flowmeter_sim_id=PIPE_2_S1 -e flowmeter_cloud_id=pipe2-sensor1 --name fw4 fw:1.4
        docker run --detach -e flowmeter_sim_id=PIPE_2_S2 -e flowmeter_cloud_id=pipe2-sensor2 --name fw5 fw:1.4
        docker run --detach -e flowmeter_sim_id=TAP_1 -e flowmeter_cloud_id=pipe2-sensor3 --name fw6 fw:1.4
        docker run --detach -e flowmeter_sim_id=PIPE_3_S1 -e flowmeter_cloud_id=pipe3-sensor1 --name fw7 fw:1.4
        docker run --detach -e flowmeter_sim_id=PIPE_3_S2 -e flowmeter_cloud_id=pipe3-sensor2 --name fw8 fw:1.4
        docker run --detach -e flowmeter_sim_id=TAP_2 -e flowmeter_cloud_id=pipe3-sensor3 --name fw9 fw:1.4
        docker run --detach -e flowmeter_sim_id=PIPE_4_S1 -e flowmeter_cloud_id=pipe4-sensor1 --name fw10 fw:1.4
        docker run --detach -e flowmeter_sim_id=PIPE_4_S2 -e flowmeter_cloud_id=pipe4-sensor2 --name fw11 fw:1.4
        docker run --detach -e flowmeter_sim_id=TAP_3 -e flowmeter_cloud_id=pipe4-sensor3 --name fw12 fw:1.4
fi
