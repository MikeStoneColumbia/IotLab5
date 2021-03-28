import machine
from machine import Pin
import time

p13 = Pin(13, Pin.IN)
prev = p13.value()

#def printer(p):
#    p.irq(trigger=0)
#    time.sleep_ms(100)
#    if p.value() == 0:
#        print(p.value())
#    p.irq(trigger=Pin.IRQ_FALLING, handler=printer)


def printer(p):
    p.irq(trigger=0)
    time.sleep_ms(100)
    global prev
    if p.value() == (prev):
        prev = not prev
        print(prev)
    p.irq(trigger=3, handler=printer)

def check():

    p13.irq(trigger=3, handler=printer)

    while(1):
        pass
#        if p13.value() != prev:
#            prev = p13.value()
#            print(prev)
#            time.sleep_ms(10)
