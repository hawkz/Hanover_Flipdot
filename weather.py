#!/usr/bin/python
# coding: utf-8 

# Weather forcast. This script uses OpenWeatherMap as data source.
# In order to use it, you need to create an account to obtain an key.

# You also need to install pyowm via the command : pip install pyowm

import pyowm
import time
from hanover_flipdot import display
from hanover_flipdot import fonts

API_KEY = "YOUR_API_KEY"
CITY = 'Mons'
COUNTRY = 'be'

display = display.Display("/dev/tty.wchusbserial1d1140", fonts.unscii_thin, False, True)
owm = pyowm.OWM(API_KEY)

def current_weather():
    observation = owm.weather_at_place('%s,%s'%(CITY, COUNTRY))
    w = observation.get_weather()

    display.erase_all()
    display.write_first_line( "TMP: %s%sC"%(w.get_temperature('celsius')['temp'], chr(0xb0)))
    display.write_second_line("HUM: %s%%"%w.get_humidity())
    display.send()

def date_time():
    display.erase_all()
    for i in range(30):
        display.write_first_line(time.strftime("%H:%M:%S"), column = 4)
        display.write_second_line(time.strftime("%a %d %b %Y"), column = 0)
        display.send()
        time.sleep(1)

while True:
    current_weather()
    time.sleep(20)
    date_time()
    time.sleep(1)
