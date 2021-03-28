import machine
from machine import Pin
import time
import ssd1306

pos = 3
states = 4
# there's 3 positions to change, and one extra state where nothing is edited
# for ...
# pos % 4 = 0: edit hour
# pos % 4 = 1: edit minute
# pos % 4 = 2: edit second
# pos % 4 = 3: disable editing

btn_a = Pin(0, Pin.IN)
btn_b = Pin(13, Pin.IN)
btn_c = Pin(2, Pin.IN)
adc = machine.ADC(0)
slp_t = 0
light_en = 0
rtc = machine.RTC()
rtc.datetime((2020, 2, 5, 2, 16, 0, 0, 0))

def press_a(p):
    # enables and cycles through values to be changed
    p.irq(trigger=0)
    delay = 20
    time.sleep_ms(delay)
    global pos
    if p.value() == 0:
        print("a pressed!")
        pos += 1
        if pos % states == 3:
            btn_b.irq(trigger=0)
            #btn_c.irq(trigger=0)
        else:
            btn_b.irq(trigger=Pin.IRQ_FALLING, handler=press_b)
            #btn_c.irq(trigger=Pin.IRQ_FALLING, handler=press_c)
    p.irq(trigger=Pin.IRQ_FALLING, handler=press_a)
    global slp_t
    slp_t = abs(slp_t - delay)
    # Just in case the sleep time tries to go negative

def press_b(p):
    # raises the value of the selected time, and 
    p.irq(trigger=0)
    delay = 20
    time.sleep_ms(delay)
    if p.value() == 0:
        print("b pressed!")
        posi = (pos % states) + 4
        dt = rtc.datetime()
        rtc.datetime((dt[0:posi] + (dt[posi] + 1,) + dt[posi+1:]))
    p.irq(trigger=Pin.IRQ_FALLING, handler=press_b)
    global slp_t
    slp_t = abs(slp_t - delay)
    # Just in case the sleep time tries to go negative

def press_c(p):
    # lowers the value of the selected time, enables light sensor if changing the time is disabled
    # my light sensor is broken (only outputs noise between 1-3 normally, and this varies up to 30 if I touch it with my finger), so I chose to enable this function with a button
    p.irq(trigger=0)
    delay = 20
    time.sleep_ms(delay)
    if p.value() == 0:
        print("c pressed!")
        if pos % states == 3:
            global light_en
            light_en = not light_en
        else:
            posi = (pos % states) + 4
            dt = rtc.datetime()
            rtc.datetime(dt[0:posi] + (dt[posi] - 1,) + dt[posi+1:])
    p.irq(trigger=Pin.IRQ_FALLING, handler=press_c)
    global slp_t
    slp_t = abs(slp_t - delay)
    # Just in case the sleep time tries to go negative

def check():
    i2c = machine.I2C(-1, Pin(5), Pin(4))
    oled = ssd1306.SSD1306_I2C(128, 32, i2c)
    global slp_t
    slp_t = 1000
    
    btn_a.irq(trigger=Pin.IRQ_FALLING, handler=press_a)
    #btn_b.irq(trigger=Pin.IRQ_FALLING, handler=press_b)
    btn_c.irq(trigger=Pin.IRQ_FALLING, handler=press_c)

    while(1):
        dt = rtc.datetime()
        oled.fill(0)
        oled_out = '%d:%d:%d' % (dt[4], dt[5], dt[6])
        oled.text(oled_out, 0, 0)
        if pos % states == 0:
            oled.text(((oled_out.find(':')) * "_"), 0, 3)
        elif pos % states == 1:
            oled.text(((oled_out.rfind(':') - oled_out.find(':') - 1) * "_"), oled_out.find(':') * 12, 3)
        elif pos % states == 2:
            oled.text(((len(oled_out) - oled_out.rfind(':') - 2) * "_"), oled_out.rfind(':') * 12, 3)

        light_level = adc.read() * 6
        # light sensor doesn't work right, so I multiply the light value to at least make the noise's effect visible
        if light_en and light_level < 256:
            oled.contrast(light_level)
        else:
            oled.contrast(128)

        oled.show()
        time.sleep_ms(slp_t)
        slp_t = 1000


