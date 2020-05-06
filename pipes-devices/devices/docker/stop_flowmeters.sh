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
fi
