#!/bin/sh

# startup script for camcorder
# select pin
GPIO=15

# prepare the pin
if [ ! -d /sys/class/gpio/gpio${GPIO} ]; then
  echo "${GPIO}" > /sys/class/gpio/export
fi
echo "in" > /sys/class/gpio/gpio"${GPIO}"/direction

# continuously monitor current value
while true; do
  if [ 0 -eq $(cat /sys/class/gpio/gpio15/value) ]; then
    printf "high \r"
    sudo python /home/raspi/camcorder/corder.py > /home/raspi/camcorder/corder.log 2> /home/raspi/camcorder/corder_error.log &
  	exit 0
  else
  	sleep 0.01
  fi
done
