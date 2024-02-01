#!/bin/sh

arduino-cli compile -b arduino:avr:uno && arduino-cli upload -b arduino:avr:uno -p /dev/ttyACM0