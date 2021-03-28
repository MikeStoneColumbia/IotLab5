import machine
from machine import Pin
import network
import socket
import ssd1306
import time

def do_connect(essid,password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(essid,password)
        while not wlan.isconnected():
            pass
        print('network config:', wlan.ifconfig())
    else:
        print('already connected!')
        print('network config:', wlan.ifconfig())


def check():
    
    i2c = machine.I2C(-1, Pin(5), Pin(4))
    oled = ssd1306.SSD1306_I2C(128, 32, i2c)
    do_connect('Fios-wY3Fj' , 'mug95crop292jus')
    command = ""
    rtc = machine.RTC()
    rtc.datetime((2021, 3, 9, 3, 16, 0, 0, 0))
    on = 1



    addr = socket.getaddrinfo('192.168.1.204', 80)[0][-1]
    print(addr)
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    # s.setblocking(0)
    s.settimeout(0.8)

    print('listening on', addr)

    while(1):
    
        dt = rtc.datetime()
        oled.fill(0)

        if on == 0 and command != "turn screen on":
            pass
        elif command == "turn screen on":
            on = 1
            oled.text("Screen on", 0, 0)
        elif command == "turn screen off":
            on = 0
        elif command == "display time":
            oled_out = '%d:%d:%d' % (dt[4], dt[5], dt[6])
            oled.text(oled_out, 0, 0)
        else:
            oled.text(command, 0, 0)
        
        oled.show()

        try:
            (conn, address) = s.accept()
            # conn.setblocking(0)
            print("accepted ", address)
        except OSError:
            pass
            #print("Nothing")
        else:

            conn_file = conn.makefile('rwb', 0)
            while True:
                line = conn_file.readline()
                if b'GET' in line:
                    command = (line.split()[1][1:]).decode()
                    print(command)
                    command = command.replace("%20", " ")
                    print(command)
                print(line)
                if not line or line == b'\r\n':
                    break
            print("sending...")
            html = "<html><body><h1>Command \'%s\' received!</h1></body></html>" % (command)

            sent = conn.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n' + html)
            print(sent)

#            try:
#                time.sleep_ms(25)
#                rec = conn.recv(4096)
#                rec = rec.split(b'\r\n\r\n')
#
#                print(rec)
#            
#            conn.send(html)
#            except OSError:
#                print("Nothing 2.0")

        #print("hi")

        time.sleep_ms(200)
