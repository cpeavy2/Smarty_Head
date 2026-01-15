#!/usr/bin/env python3

import pigpio
import time

# GPIO pins (BCM numbering)
GPIO_TRIGGER = 18
GPIO_ECHO = 24

# Speed of sound (cm/s)
SPEED_OF_SOUND = 34300

# Connect to pigpio daemon
pi = pigpio.pi()
if not pi.connected:
    raise RuntimeError("Cannot connect to pigpiod")

# Setup pins
pi.set_mode(GPIO_TRIGGER, pigpio.OUTPUT)
pi.set_mode(GPIO_ECHO, pigpio.INPUT)

# Ensure trigger is low
pi.write(GPIO_TRIGGER, 0)
time.sleep(0.1)


def distance(timeout=0.04):
    """
    Measure distance in meters.
    timeout prevents infinite hangs.
    """

    # Send 10µs trigger pulse
    pi.write(GPIO_TRIGGER, 1)
    time.sleep(0.00001)
    pi.write(GPIO_TRIGGER, 0)

    start_time = time.time()

    # Wait for echo to go high
    while pi.read(GPIO_ECHO) == 0:
        if time.time() - start_time > timeout:
            return None

    pulse_start = time.time()

    # Wait for echo to go low
    while pi.read(GPIO_ECHO) == 1:
        if time.time() - pulse_start > timeout:
            return None

    pulse_end = time.time()

    # Time difference
    pulse_duration = pulse_end - pulse_start

    # Distance in meters
    distance_m = (pulse_duration * SPEED_OF_SOUND) / 2 / 100

    return distance_m


if __name__ == "__main__":
    try:
        while True:
            dist = distance()
            if dist is None:
                print("Out of range / timeout")
            else:
                print(f"Measured Distance = {dist:.2f} m")

            time.sleep(1)

    except KeyboardInterrupt:
        print("Measurement stopped by User")

    finally:
        pi.stop()
