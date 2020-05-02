#!/bin/bash

if [ `whoami` != 'root' ]; then
        echo Please run this script as root 
        exit
else  
        echo Stopping fwX containers
        docker container start fw1
        docker container start fw2
        docker container start fw3
        docker container start fw4
        docker container start fw5
        docker container start fw6
        docker container start fw7
        docker container start fw8
fi
