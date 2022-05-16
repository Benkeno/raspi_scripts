#!/usr/bin/python
# -*- coding: utf-8 -*-

from RPi import GPIO
from time import sleep
import sys

# A GPIO pin number that connected with a fan controller
FAN_GPIO = 18 # BCM number

#
PWM_FREQ = 25  # [Hz] Change this value if fan has strange behavior

# A time period of monitoring the SoC temperature
INTERVAL = 2 # in seconds (greater than 0)

# Uses this load value when the SoC temperature is less than minimum working temperature
IDLE_LOAD = 0

# Each step must be a tuple that have temperature and fans load ratio
# The tempratures unit is in celcius degrees. (0~100)
# The fans load ratios unit is in percentage. (0~100)
TEMP_LOAD_STEPS = [
    (55, 40),
    (58, 50),
    (60, 80),
    (63, 100)
]

# Fan speed will change only of the difference of temperature is higher than hysteresis
IDLE_HYST = 1

# Validate steps
if len(TEMP_LOAD_STEPS) < 1:
    sys.stderr.write("There is no given steps.\n")
    exit(1)
for step_idx, (step_temp, step_load) in enumerate(TEMP_LOAD_STEPS):
    if not 0 <= step_temp <= 100:
        sys.stderr.write("The temperature value in the step %s is not between 0 and 100.\n" % step_idx)
        exit(1)
    if not 0 <= step_load <= 100:
        sys.stderr.write("The load value in the step %s is not between 0 and 100.\n" % step_idx)
        exit(1)
    if step_idx > 0:
        prev_step_temp, prev_step_load = TEMP_LOAD_STEPS[step_idx-1]
        if step_temp < prev_step_temp:
            sys.stderr.write("The temperature value in the step %s is smaller than previous steps one.\n" % step_idx)
            exit(1)
        if step_load < prev_step_load:
            sys.stderr.write("The load value in the step %s is smaller than previous steps one.\n" % step_idx)
            exit(1)

# Setup GPIO pin
GPIO.setmode(GPIO.BCM)
GPIO.setup(FAN_GPIO, GPIO.OUT)
fan = GPIO.PWM(FAN_GPIO, PWM_FREQ)
fan.start(100)
is_idle = False

# Start loop
try:
    while True:
        # Wait until next refresh
        sleep(INTERVAL)

        # Read CPU temperature
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as file:
            temp = float(file.read()) / 1000

        min_temp, min_load = TEMP_LOAD_STEPS[0]
        if temp < min_temp:
            if not is_idle:
                if temp >= min_temp - IDLE_HYST:
                    fan.ChangeDutyCycle(min_load)
                    continue
                else:
                    is_idle = True
                    fan.ChangeDutyCycle(IDLE_LOAD)
        else:
            if is_idle:
                if temp < min_temp + IDLE_HYST:
                    continue
                else:
                    is_idle = False
            # load = min_load
            load = min_load
            for step_idx, (step_temp, step_load) in enumerate(TEMP_LOAD_STEPS):
                if step_idx == 0:
                    continue
                prev_temp, prev_load = TEMP_LOAD_STEPS[step_idx-1]
                if prev_temp <= temp < step_temp:
                    percentage = (temp - prev_temp) / (step_temp - prev_temp)
                    load = prev_load + percentage * (step_load - prev_load)
                    # print("pt:%s pl:%s st:%s sl:%s P:%s"% (prev_temp, prev_load, step_temp, step_load, percentage))
                    break
                elif temp >= step_temp and step_idx + 1 == len(TEMP_LOAD_STEPS):
                    load = step_load
            fan.ChangeDutyCycle(load)
            #print("T:%s L:%s" % (temp, load))

# On keyboard interrupt occurs
except KeyboardInterrupt:
    fan.stop()
    GPIO.cleanup()
    exit()