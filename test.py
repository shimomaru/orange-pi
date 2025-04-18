#!/bin/bash

import wiringpi
from wiringpi import GPIO

wiringpi.wiringPiSetup()
wiringpi.pinMode(2, GPIO.OUTPUT)
wiringpi.digitalWrite(2, GPIO.HIGH)
