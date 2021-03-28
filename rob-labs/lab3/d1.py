import machine
from machine import Pin
import network
import urequests
import socket
import ssd1306

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

    # jsonData={'content type':'application/json','content length':'0'}
    # is this ^ outdated?
    
    # simple json. It only uses IP which may be inaccurate, but it finds my location within less than a kilometer
    jsonData={}
    
    # wifi json
    # jsonData={"considerIp": "false", "wifiAccessPoints": [
    #    {"macAddress": "B8.F8.53.AE.34.F4"}
    #    {"macAddress": 

    url = 'https://www.googleapis.com/geolocation/v1/geolocate?key=AIzaSyBz5g_3h12MrFEADAM89VAYdMz78QaDbTc'
    
    
    r_json=urequests.post(url, json=jsonData)
    r = r_json.json()
    print(r)
    lat = r['location']['lat']
    lng = r['location']['lng']
    
    oled.fill(0)

    oled_out = 'lat: %f' % (lat)
    oled.text(oled_out, 0, 0)
    oled_out = 'lng: %f' % (lng)
    oled.text(oled_out, 0, 8)
    oled.show()
