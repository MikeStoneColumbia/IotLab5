import machine
from machine import Pin
import time



def check():
    p13 = Pin(13, Pin.IN)
    prev = p13.value()

    while(1):
        if p13.value() != prev:
            time.sleep_ms(20)
            prev = p13.value()
            print(prev)
