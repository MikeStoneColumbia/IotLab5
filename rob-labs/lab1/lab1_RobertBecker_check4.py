import machine
from machine import Pin
import time

p15 = Pin(15)
p12 = Pin(12)
p13 = Pin(13, Pin.IN)

pwm15 = machine.PWM(p15)
pwm12 = machine.PWM(p12)

adc = machine.ADC(0)
p2 = Pin(2, Pin.OUT)

enable = 0

def enabler(p):
    p.irq(trigger=0)
    time.sleep_ms(100)
    global enable
    if p.value() == (enable):
        enable = not enable
    p.irq(trigger=3, handler=enabler)


def disabler(p):
    p.irq(trigger=0)
    time.sleep_ms(10)
    if p.value() == 1:
        enable = 0
    p.irq(trigger=Pin.IRQ_RISING, handler=printer)

def check():


    p13.irq(trigger=3, handler=enabler)

    while True:
        if enable:
            light_level = adc.read()
            pwm15.duty(light_level * 20)
            pwm12.duty(light_level * 20)
            # Multiplying by 20 since my sensor isn't working right
        else:
            pwm15.duty(0)
            pwm12.duty(0)

        time.sleep_ms(100)
