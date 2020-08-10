#!/bin/bash

pid=$(ps -ef | grep '[0-9] sudo python3 run.py' | awk '{print $2}')

if [ -n "$pid" ]; then
    sudo kill $pid
fi

if [ -d "/home/ubuntu/reservation-system/" ]; then
    sudo rm -r /home/ubuntu/reservation-system
fi
# if [ -d "/home/ubuntu/reservation-system/customer" ]; then
#     sudo rm -r /home/ubuntu/reservation-system/customer
# fi
# if [ -d "/home/ubuntu/reservation-system/admin" ]; then
#     sudo rm -r /home/ubuntu/reservation-system/admin
# fi
# if [ -d "/home/ubuntu/reservation-system/templates" ]; then
#     sudo rm -r /home/ubuntu/reservation-system/templates
# fi
# if [ -f "/home/ubuntu/reservation-system/config.ini" ]; then
#     sudo rm /home/ubuntu/reservation-system/config.ini
# fi