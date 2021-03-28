import machine
from machine import Pin
import time

p15 = Pin(15)
p12 = Pin(12)

pwm15 = machine.PWM(p15)
pwm12 = machine.PWM(p12)

adc = machine.ADC(0)
p2 = Pin(2, Pin.OUT)

def check():
    while True:
        light_level = adc.read()
        pwm15.duty(light_level * 20)
        pwm12.duty(light_level * 20)
        time.sleep_ms(100)
        # Multiplying by 20 since my sensor isn't working right

