import machine
from machine import Pin
import network
import urequests
import socket
import time
import ssd1306

btn_a = Pin(0, Pin.IN)
send_tweet = 0

# sets global var when button triggers the interrupt
# this is so the program doesn't get stuck in an interrupt while it waits to send

def press_a(p):
    p.irq(trigger=0)
    time.sleep_ms(20)
    if p.value() == 0:
        print("a pressed!")
        global send_tweet
        send_tweet = 1
    p.irq(trigger=Pin.IRQ_FALLING, handler=press_a)


# creates wifi connection

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

    global send_tweet

    btn_a.irq(trigger=Pin.IRQ_FALLING, handler=press_a)

    url = "https://api.thingspeak.com/apps/thingtweet/1/statuses/update"
    status = "Wouldn't it be siiick if Ori was in Super Smash Bros? I think it would. - ESP8266, but again" 
    jsonData={'api_key': '6K3EP3OBQQ538PGW', 'status': status}
    
    while(1):

        oled.fill(0)
        oled.show()

        # Device will send one tweet at a time when it sees the button was pushed. 
        if send_tweet == 1:
            r_json=urequests.post(url, json=jsonData)
            r = r_json.json()
            send_tweet = 0

            print(r)
            if r == 1:
                oled.text("Tweet sent!", 0, 0)
            else:
                oled.text("Tweet failed", 0, 0)
            oled.show()

            time.sleep(5)
        
        time.sleep(1/12)
