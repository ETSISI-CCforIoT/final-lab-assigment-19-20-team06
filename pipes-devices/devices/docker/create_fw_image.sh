#!/bin/bash

if [ `whoami` != 'root' ]; then
        echo Please run this script as root
        exit
else
        echo Creating Docker image fw:1.4
        docker build --tag fw:1.4
fi
