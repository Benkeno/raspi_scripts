#! /usr/bin/python
# coding: utf-8

# Display connected to PIN 5 and 6 (SCA, SCL) 
import time


import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import subprocess

# Raspberry Pi pin configuration:
RST = None     # on the PiOLED this pin isnt used

# 128x64 OLED I2C display with hardware I2C:
disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)

# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0,0,width,height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height-padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0


# Load default font.
font = ImageFont.load_default()

# Alternatively load a TTF font.  Make sure the .ttf font file is in the same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
  #font = ImageFont.truetype('Boge.ttf', 8)

while True:

    # Draw a black filled box to clear the image.
    draw.rectangle((0,0,width,height), outline=0, fill=0)

    # Shell scripts for system monitoring from here : https://unix.stackexchange.com/questions/119126/command-to-display-memor>
    
    cmd = "hostname -a"                                                             # enter the command to 'terminal'
    HOST = subprocess.check_output(cmd, shell = True )                              # save the output to variable 
    cmd = "hostname -I | cut -d\' \' -f1"                                           # to get a specific value with cut awk etc..
    #cmd = "hostname -I |cut -f 2 -d ' '"
    IP = subprocess.check_output(cmd, shell = True )
    cmd = "top -bn1 | grep load | awk '{printf \"CPU USE: %.2f\", $(NF-2)}'"
    CPU = subprocess.check_output(cmd, shell = True )
    cmd = "free -m | awk 'NR==2{printf \"RAM: %s/%s MB %.2f%%\", $3,$2,$3*100/$2 }'"
    MemUsage = subprocess.check_output(cmd, shell = True )
    cmd = "df -h | awk '$NF==\"/\"{printf \"DISK: %d/%d GB %s\", $3,$2,$5}'"
    Disk = subprocess.check_output(cmd, shell = True )
    cmd = "vcgencmd measure_temp |cut -f 2 -d '='"
    temp = subprocess.check_output(cmd, shell = True )
    cmd =  "vnstat -ru 1 --oneline | cut -f7 -d ';'"
    MBOUT = subprocess.check_output(cmd, shell = True )

    # Write lines of text.
    draw.text((x, top+1),       "HOST: " + str(HOST,'utf-8'),  font=font, fill=255)
    draw.text((x, top+12),  "IP: " + str(IP,'utf-8'), font=font, fill=255)
    draw.text((x, top+22),  str(CPU,'utf-8') + " " + str(temp,'utf-8') , font=font, fill=255)
    draw.text((x, top+32), str(MemUsage,'utf-8'), font=font, fill=255)
    draw.text((x, top+42), str(Disk,'utf-8'), font=font, fill=255)
    draw.text((x, top+52), "NET: " + str(MBOUT,'utf-8'), font=font, fill=255)
    #draw.text((x, top+16),    str(MemUsage),  font=font, fill=255)
    #draw.text((x, top+25),    str(Disk),  font=font, fill=255)

    # Display image.
    disp.image(image)
    disp.display()
    time.sleep(.1)

