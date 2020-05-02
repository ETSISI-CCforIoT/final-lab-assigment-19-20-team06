#!/bin/bash

if [ `whoami` != 'root' ]; then
        echo Please run this script as root 
        exit
else  
        echo Removing fwX containers
        docker container rm fw1
        docker container rm fw2
        docker container rm fw3
        docker container rm fw4
        docker container rm fw5
        docker container rm fw6
        docker container rm fw7
        docker container rm fw8
fi
