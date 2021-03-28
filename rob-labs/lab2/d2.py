import machine
from machine import Pin
import time
import ssd1306

pos = 6
states = 7
# there's 3 positions to change the time, 3 to set the alarm, and one extra state where nothing is edited
# for ...
# pos % 7 = 0: edit hour
# pos % 7 = 1: edit minute
# pos % 7 = 2: edit second
# pos % 7 = 3: edit alarm hour
# pos % 7 = 4: edit alarm minute
# pos % 7 = 5: edit alarm second
# pos % 7 = 6: disable editing

btn_a = Pin(0, Pin.IN)
btn_b = Pin(13, Pin.IN)
btn_c = Pin(2, Pin.IN)

# initialize buzzer pin
p12 = Pin(12)
pwm12 = machine.PWM(p12)

adc = machine.ADC(0)
slp_t = 0
light_en = 0
rtc = machine.RTC()
rtc.datetime((2020, 2, 5, 2, 16, 0, 0, 0))
alarm_hms = (rtc.datetime()[4], 0, 15)
print(alarm_hms)

def press_a(p):
    # enables and cycles through values to be changed
    p.irq(trigger=0)
    delay = 20
    time.sleep_ms(delay)
    global pos
    if p.value() == 0:
        print("a pressed!")
        pos += 1
        if pos % states == 6:
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
    # raises the value of the selected time 
    p.irq(trigger=0)
    delay = 20
    time.sleep_ms(delay)
    if p.value() == 0:
        print("b pressed!")
        if pos % states > 2:
            global alarm_hms
            posi = (pos % states) - 3
            # this will be triggered during pos of 3, 4, and 5 (alarm)
            # subtract 3 to access the correct index
            if posi == 0 and alarm_hms[0] == 23:
                alarm_hms = (0,) + alarm_hms[1:]
            elif posi != 0 and alarm_hms[posi] == 59:
                alarm_hms = alarm_hms[0:posi] + (0,) + alarm_hms[posi+1:]
            else:
                alarm_hms = alarm_hms[0:posi] + (alarm_hms[posi] + 1,) + alarm_hms[posi+1:]
        else:
            posi = (pos % states) + 4
            # this will be triggered during pos of 0, 1, and 2 (clock)
            # rtc.datetime() has hours starting in index 4, so we add 4 to the modulo
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
        if pos % states == 6:
            global light_en
            light_en = not light_en
        elif pos % states > 2:
            global alarm_hms
            posi = (pos % states) - 3
            # this will be triggered during pos of 3, 4, and 5 (alarm)
            # subtract 3 to access the correct index
            if posi == 0 and alarm_hms[0] == 0:
                alarm_hms = (23,) + alarm_hms[1:]
            elif posi != 0 and alarm_hms[posi] == 0:
                alarm_hms = alarm_hms[0:posi] + (59,) + alarm_hms[posi+1:]
            else:
                alarm_hms = alarm_hms[0:posi] + (alarm_hms[posi] - 1,) + alarm_hms[posi+1:]
        else:
            # this will be triggered during pos of 0, 1, and 2 (clock)
            # rtc.datetime() has hours starting in index 4, so we add 4 to the modulo
            posi = (pos % states) + 4
            dt = rtc.datetime()
            rtc.datetime(dt[0:posi] + (dt[posi] - 1,) + dt[posi+1:])
    p.irq(trigger=Pin.IRQ_FALLING, handler=press_c)
    global slp_t
    slp_t = abs(slp_t - delay)
    # Just in case the sleep time tries to go negative

def is_buzzing(dt):
    # buzzer rings for 10 seconds once the daily time reaches it
    dt_hms = dt[4:7]

    alarm_sec = alarm_hms[0] * 3600 + alarm_hms[1] * 60 + alarm_hms[2]
    dt_sec = dt_hms[0] * 3600 + dt_hms[1] * 60 + dt_hms[2]

    diff = dt_sec - alarm_sec
    #print(dt_hms)
    #print(diff)

    if diff > 0 and diff < 10:
        return True
    else:
        return False



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
        if pos % states < 3 or pos % states == 6:
            # outputs the current time
            oled_out = '%d:%d:%d' % (dt[4], dt[5], dt[6])
        else:
            # outputs the alarm's time
            oled_out = '%d:%d:%d' % (alarm_hms[0], alarm_hms[1], alarm_hms[2])
            oled.text("Set alarm time", 0, 14)
        oled.text(oled_out, 0, 0)
        if pos % states == 0 or pos % states == 3:
            oled.text(((oled_out.find(':')) * "_"), 0, 3)
        elif pos % states == 1 or pos % states == 4:
            oled.text(((oled_out.rfind(':') - oled_out.find(':') - 1) * "_"), (oled_out.find(':') + 1) * 8, 2)
        elif pos % states == 2 or pos % states == 5:
            oled.text(((len(oled_out) - oled_out.rfind(':') - 1) * "_"), (oled_out.rfind(':') + 1) * 8, 2)

        light_level = adc.read() * 6
        # light sensor doesn't work right, so I multiply the light value to at least make the noise's effect visible
        if light_en and light_level < 256:
            oled.contrast(light_level)
        else:
            oled.contrast(128)

        if is_buzzing(dt):
            pwm12.duty(512)
            oled.text("Alarm triggered!", 0, 23)
            # print("buzz buzz!")
        else:
            pwm12.duty(0)

        oled.show()
        time.sleep_ms(slp_t)
        slp_t = 1000


