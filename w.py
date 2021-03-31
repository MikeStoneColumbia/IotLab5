import network
import ustruct
import socket
import select
from ssd1306 import SSD1306_I2C
from ubinascii import hexlify
from machine import Pin, I2C, ADC, RTC
from time import sleep_ms

i2c = I2C(-1, Pin(5), Pin(4))
oled = SSD1306_I2C(128, 32, i2c)
old_weather = []
old_tweet = ''
show_clock = False;
time_set = False;
light = ADC(0)
rtc = RTC()
ptr=0
a = Pin(0, Pin.IN, Pin.PULL_UP)
b = Pin(13, Pin.IN)
c = Pin(2, Pin.IN, Pin.PULL_UP)

date = []

def greeting():
    oled.fill(0)
    oled.text('smart watch',0,0)
    oled.show()

greeting()

def format_time(time):
    time = time.split(':')
    year = int(time[0])
    month = int(time[1])
    day = int(time[2])
    hour = int(time[3])
    minute = int(time[4])
    second = int(time[5])
    rtc.datetime((year, month, day, 1,hour,minute,second,0))

def m_mode():
    global time_set
    global date
    global show_clock
    time_set = False
    show_clock = True
    str_t = ""
    for t in date:
        t += str(t) + ':'
    format_time(t)
    time_functions()


def disable(btn):
    btn.irq(handler=None)

def disable_all():
    a.irq(trigger=Pin.IRQ_FALLING, handler=None)
    b.irq(trigger=Pin.IRQ_FALLING, handler=None)
    c.irq(trigger=Pin.IRQ_FALLING, handler=None)

def change_clk(date):
    global ptr
    av = a.value()
    cv = c.value()
    sleep_ms(14)
    av2 = a.value()
    cv2 = c.value()
    if av and not av2:
        date[ptr] += 1
    if cv and not cv2:
        ptr += 1
        if ptr >= 6:
            ptr = 0
    
def display_d(date):
    oled.fill(0)
    oled.text(str(date[0])+'/'+str(date[1])+'/'+str(date[2]), 0, 0)
    oled.text(str(date[3])+':'+str(date[4])+':'+str(date[5]), 0, 16)
    oled.show()   

def set_alarm(pin):
    pass

def set_time(pin):
    global time_set
    global show_clock
    global date
    date = list(x for x in rtc.datetime()[0:7])
    del date[3]
    time_set = True
    show_clock = False
    b.irq(trigger=Pin.IRQ_FALLING,handler=m_mode)
    c.irq(trigger=Pin.IRQ_FALLING,handler=None)
        
def feature_mode():
    global show_clock
    c.irq(trigger=Pin.IRQ_FALLING, handler=show_old_weather) 
    a.irq(trigger=Pin.IRQ_FALLING, handler=show_old_tweet)
    show_clock = False
    greeting()

def show_old_weather(pin):
    global show_clock
    show_clock = False
    oled.fill(0)
    if len(old_weather) == 0:
        show('no weather',0,0)
    else:
        show(old_weather[0],0,0)
        show(old_weather[1],0,16)

def show_old_tweet(pin):
    global show_clock
    show_clock = False
    oled.fill(0)
    if len(old_tweet) == 0:
        show('no tweets',0,0)
    else:
        show(old_tweet,0,0)

def clear_oled():
    oled.fill(0)
    oled.show()

def adjust_brightness():
    oled.contrast(int(255 * (light.read()/1024))) 

def show(msg,xcor,ycor):
    oled.text(msg,xcor,ycor)
    oled.show()

def do_connect():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        sta_if.active(True)
        sta_if.connect('Fios-wY3Fj' , 'mug95crop292jus')
        while not sta_if.isconnected():
            pass
    return sta_if
wifi = do_connect()

def response(message,cl):
    cl.send('HTTP/1.0 200 OK\r\n\r\n'.encode())
    cl.send(message.encode())

def update_time():
    date = []
    year_month_date = ''
    hour_min_seconds = ''
    date = list(str(x) for x in rtc.datetime()[0:7])
    year_month_date = date[0] + '/' + date[1] + '/' + date[2]
    hour_min_seconds = date[4] + ':' + date[5] + ':' + date[6]
    oled.fill(0)
    oled.text(year_month_date,0,0)
    oled.text(hour_min_seconds, 0, 10)
    oled.show()

def time_functions():
    c.irq(trigger=Pin.IRQ_FALLING, handler=set_time)
    a.irq(trigger=Pin.IRQ_FALLING, handler=set_alarm)
    b.irq(trigger=Pin.IRQ_FALLING, handler=feature_mode)


def check():
    addr = socket.getaddrinfo('192.168.1.204', 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    read_list = [s]
    feature_mode()
    s.settimeout(0.8)
    print("listening on: ", addr)
    
    global old_weather
    global old_tweet
    global show_clock
    global time_set
    
    while True:
        try:
            (soc, address) = s.accept()
            print("accepted ", address)
        except OSError:
            pass
        else:
            print('before recv2')
            msg = soc.recv(2048).decode()
            print(msg, 'hi')
            data = msg.split('\r\n')[-1].split('\"')
            desc = data[-2]
            time = str(data[3])
            com = data[7]
            if com == 'time':
                show_clock = True
                time_functions()
                format_time(time)
                response('{\'response\': \'time success\'}',soc)
            elif com == 'weather':
                a.irq()
                show_clock = False
                oled.fill(0)
                desc = desc.split('%')
                old_weather = desc
                show(desc[0],0,0)
                show(desc[1],0,16)
                response('{\'response\': \' weather success\'}',soc)
            elif com == 'tweet':
                show_clock = False
                oled.fill(0)
                old_tweet = desc
                show(desc,0,0)
                response('{\'response\': \' tweet success\'}',soc)
            else:
                response('{\'response\': \'invalid\'}',soc)
            soc.close()
        if show_clock:
            update_time()
        elif time_set:
            display_d(date)
            change_clk(date)
            
        sleep_ms(200)