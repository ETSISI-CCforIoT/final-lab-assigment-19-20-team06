#!/bin/bash

if [ `whoami` != 'root' ]; then
        echo Please run this script as root 
        exit
else  
        echo Stopping fwX containers
        docker container stop fw1
        docker container stop fw2
        docker container stop fw3
        docker container stop fw4
        docker container stop fw5
        docker container stop fw6
        docker container stop fw7
        docker container stop fw8
        docker container stop fw9
        docker container stop fw10
        docker container stop fw11
        docker container stop fw12
fi
