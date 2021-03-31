import machine
from machine import Pin
import time
import ssd1306
import urequests
import ujson

hspi = machine.SPI(1, baudrate=1500000, polarity=1, phase=1)
cs = Pin(15, Pin.OUT)
a = Pin(0, Pin.IN, Pin.PULL_UP)
cs.value(1)
test = 1

def check():
    i2c = machine.I2C(-1, Pin(5), Pin(4))
    oled = ssd1306.SSD1306_I2C(128, 32, i2c)
    time.sleep_ms(50)
    samples = 91
    readings = []
    oled_out = ""

    URL = "http://ec2-18-233-162-2.compute-1.amazonaws.com"
    PORT = 8080 # The port used by the server
    


    # set data format
    cs.value(0)
    hspi.write(b'\x31\x2B') 
    cs.value(1)
    time.sleep_ms(50)

    # set power-saving features control
    cs.value(0)
    hspi.write(b'\x2d\x28')
    cs.value(1)
    time.sleep_ms(50)

    # set BW_Rate
    cs.value(0)
    hspi.write(b'\x2c\x0B')
    cs.value(1)
    time.sleep_ms(50)

    # set interrupt enable
    cs.value(0)
    hspi.write(b'\x2e\x00')
    cs.value(1)
    time.sleep_ms(50)

    # set FIFO control
    cs.value(0)
    hspi.write(b'\x38\x9F')
    cs.value(1)
    time.sleep_ms(50)
    
    while(1):
        oled.fill(0)
        
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
        
        if samples <= 90:
            bufx = ((bufx1[0]<<8) + bufx0[0])/256
            bufy = ((bufy1[0]<<8) + bufy0[0])/256
    
            print(bufx, bufy)
            readings.append(bufx)
            readings.append(bufy)
            
            if samples == 90:
                message = {"letter": 'a', "readings" : readings}
                response = urequests.post("{}:{}/{}".format(URL, PORT, 'train'), json=ujson.dumps(message), headers = {'content-type': 'application/json'})
                # if(test):
                #     oled_out = ujson.load(response.content)["result"]
                # else:
                #     oled_out = response.content
                oled_out = response.content
                print(oled_out)
                
        if a.value() == 0:
            
            samples = 0
            readings = []
            
        
        # print(bufx1, bufx0)
        # print(bufy1, bufy0)
        
        # Justify bit will be 1 when the number is negative, justify bit is rightmost one in buf1


        # if bufx > 2:
        #     if bufx < 255.5:
        #         xy[0] += 1
        # elif bufx > 0.5:
        #     xy[0] -= 1

        # if bufy > 2:
        #     if bufy < 255.5:
        #         xy[1] -= 1
        # elif bufy > 0.5:
        #     xy[1] += 1

        # # text will reappear on the opposite side of the screen once it fully disappears
        # if xy[0] > 127:
        #     xy[0] = 0
        # elif xy[0] < 0:
        #     xy[0] = 127
        # if xy[1] > 31:
        #     xy[1] = 0
        # elif xy[1] < 0:
        #     xy[1] = 31
        
        # oled.text("hello", xy[0], xy[1])
        
        samples += 1
        oled.text(oled_out, 0, 0)
        oled.show()
        
        # screen updates at 12fps
        time.sleep(1/30)
