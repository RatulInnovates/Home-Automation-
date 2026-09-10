from gpiozero import MotionSensor
import time

# Initialize PIR sensor on GPIO 27
pir = MotionSensor(27)

print("Testing PIR sensor on GPIO 27... Wave your hand!")

try:
    while True:
        pir.wait_for_motion()
        print("Motion detected!")
        pir.wait_for_no_motion()
        print("Area clear.")
except KeyboardInterrupt:
    print("\nTest finished.")