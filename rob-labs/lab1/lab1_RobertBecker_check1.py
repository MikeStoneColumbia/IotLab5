import machine
from machine import Pin
import time

p0 = Pin(0, Pin.OUT)
p2 = Pin(2, Pin.OUT)
ratio = 5

def toggle(p):
    p.value(not p.value())

def check():
    while (True):
        for i in range(ratio):
            toggle(p0)
            time.sleep_ms(100)
        toggle(p2)
