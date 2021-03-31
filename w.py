import network
import urequests
import socket
from ssd1306 import SSD1306_I2C
from machine import Pin, I2C, ADC, RTC, SPI
from time import sleep_ms
import urequests
import ujson

modes = ['greeting','weather', 'tweet', 'time', 'alarm', 'letters','showtime']
mode_ptr = 0
hspi = SPI(1, baudrate=1500000, polarity=1, phase=1)
cs = Pin(15, Pin.OUT)
cs.value(1)

sleep_ms(50)

URL = "http://ec2-18-233-162-2.compute-1.amazonaws.com"
PORT = 8080 # The port used by the server

# set data format
cs.value(0)
hspi.write(b'\x31\x2B') 
cs.value(1)
sleep_ms(50)

# set power-saving features control
cs.value(0)
hspi.write(b'\x2d\x28')
cs.value(1)
sleep_ms(50)

# set BW_Rate
cs.value(0)
hspi.write(b'\x2c\x0B')
cs.value(1)
sleep_ms(50)

# set interrupt enable
cs.value(0)
hspi.write(b'\x2e\x00')
cs.value(1)
sleep_ms(50)

# set FIFO control
cs.value(0)
hspi.write(b'\x38\x9F')
cs.value(1)
sleep_ms(50)

i2c = I2C(-1, Pin(5), Pin(4))
oled = SSD1306_I2C(128, 32, i2c)
old_weather = []
old_tweet = ''
show_clock = False;
time_set = False;
light = ADC(0)
rtc = RTC()
ptr=0
alarm = []
a = Pin(0, Pin.IN, Pin.PULL_UP)
b = Pin(13, Pin.IN)
c = Pin(2, Pin.IN, Pin.PULL_UP)
buzz = Pin(12,Pin.OUT)
buzz.off()
set_alarm = []

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
    print(av, av2)
    print(cv, cv2)
    if not av and not av2:
        date[ptr] += 1
    if not cv and not cv2:
        ptr += 1
        if ptr >= 6:
            ptr = 0
    
def display_d(date):
    oled.fill(0)
    oled.text(str(date[0])+'/'+str(date[1])+'/'+str(date[2]), 0, 0)
    oled.text(str(date[3])+':'+str(date[4])+':'+str(date[5]), 0, 16)
    oled.show()   

def cycle_mode(pin):
    global mode_ptr
    global modes
    global show_clock
    global date 
    global alarm
    global set_alarm
    curr_time = list(x for x in rtc.datetime()[0:7])
    del curr_time[3]

    if modes[mode_ptr] == 'time':
        str_t = ""
        for t in date:
            str_t += str(t) + ':'
        format_time(str_t)
   
    if modes[mode_ptr] == 'alarm' and alarm > curr_time:
         set_alarm = alarm
    
    mode_ptr += 1
    show_clock = False
    if modes[mode_ptr] == 'greeting':
        greeting()
    elif modes[mode_ptr] == 'weather':
        show_old_weather()
    elif modes[mode_ptr] == 'tweet':
        show_old_tweet()
    elif modes[mode_ptr] == 'time' or modes[mode_ptr] == 'alarm':  
        date = list(x for x in rtc.datetime()[0:7])
        del date[3]
        display_d(date)
    elif modes[mode_ptr] == 'letters':
        print('press c to detect letters')
        pass
    elif modes[mode_ptr] == 'showtime':
        show_clock = True
        mode_ptr = -1

def update_val(pin):
    global mode_ptr
    global modes
    global ptr
    global alarm
    c.irq(trigger=0)
    print(mode_ptr)
    if modes[mode_ptr] == 'letters':
        global cs
        readings = []
        for i in range(36):
            print('send lets')
            
            # print("a", a.value())
            # print("b", b.value())
            # print("c", c.value())
            
    
            bufx0 = bytearray(1)
            bufx1 = bytearray(1)
            bufy0 = bytearray(1)
            bufy1 = bytearray(1)
            bufz0 = bytearray(1)
            bufz1 = bytearray(1)
        
            # read from registers
    
            cs.value(0)
            hspi.write(b'\xb2')
            hspi.readinto(bufx0)
            cs.value(1)
    
            cs.value(0)
            hspi.write(b'\xb3')
            hspi.readinto(bufx1)
            cs.value(1)
    
            cs.value(0)
            hspi.write(b'\xb4')
            hspi.readinto(bufy0)
            cs.value(1)
    
            cs.value(0)
            hspi.write(b'\xb5')
            hspi.readinto(bufy1)
            cs.value(1) 
            
            cs.value(0)
            hspi.write(b'\xb6')
            hspi.readinto(bufz0)
            cs.value(1)
    
            cs.value(0)
            hspi.write(b'\xb7')
            hspi.readinto(bufz1)
            cs.value(1)
            
            
            bufx = ((bufx1[0]<<8) + bufx0[0])/256
            bufy = ((bufy1[0]<<8) + bufy0[0])/256
    
            print(bufx, bufy)
            readings.append(bufx)
            readings.append(bufy)
        
            # screen updates at 12fps
            sleep_ms(int(1000/12))
            
        message = {"letter": 'a', "readings" : readings}
        response = urequests.post("{}:{}/{}".format(URL, PORT, 'train'), json=ujson.dumps(message), headers = {'content-type': 'application/json'})
        print(response.content)
        show(response.content, 0,0)
        
    elif modes[mode_ptr] == 'time' or modes[mode_ptr] == 'alarm':
        sleep_ms(20)
        if c.value() == 0:
            date[ptr] += 1
            if ptr == 1 and date[ptr] > 12:
                date[ptr] = 1
            elif ptr == 2 and date[ptr] > 31:
                date[ptr] = 1
            elif ptr == 3 and date[ptr] > 23:
                date[ptr] = 0
            elif ptr == 4 and date[ptr] > 59:
                date[ptr] = 0
            elif ptr == 5 and date[ptr] > 59:
                date[ptr] = 0
            display_d(date)
            if modes[mode_ptr] == 'alarm':
                alarm = date[:]
    c.irq(trigger=Pin.IRQ_FALLING, handler=update_val) 

def mv_ptr(pin):
    global ptr
    ptr += 1
    if ptr >= 6:
        ptr = 0


def feature_mode():
    global show_clock
    c.irq(trigger=Pin.IRQ_FALLING, handler=update_val) 
    a.irq(trigger=Pin.IRQ_FALLING, handler=cycle_mode)
    b.irq(trigger=Pin.IRQ_FALLING, handler=mv_ptr)
    show_clock = False
    greeting()

def show_old_weather():
    oled.fill(0)
    if len(old_weather) == 0:
        show('no weather',0,0)
    else:
        show(old_weather[0],0,0)
        show(old_weather[1],0,16)

def show_old_tweet():
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
    global alarm
    global set_alarm
    global a
    
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
        
        curr = list(x for x in rtc.datetime()[0:7])
        del curr[3]
                    
        while len(set_alarm) > 0 and curr > set_alarm:
            print("buzz buzz!")
            a.irq(trigger=0)
            b.irq(trigger=0)
            c.irq(trigger=0)
            buzz.on()
            if a.value() == 0:
                buzz.off()
                alarm = []
                set_alarm = []
                a.irq(trigger=Pin.IRQ_FALLING, handler=cycle_mode)
                b.irq(trigger=Pin.IRQ_FALLING, handler=mv_ptr)
                c.irq(trigger=Pin.IRQ_FALLING, handler=update_val)
        
        bufx0 = bytearray(1)
        cs.value(0)
        hspi.write(b'\xb2')
        hspi.readinto(bufx0)
        cs.value(1)
        
        if show_clock:
            update_time()
        elif time_set:
            display_d(date)
            change_clk(date)
            