from fonts import font
import lib.display
import time

d = lib.display.Display("/dev/tty.wchusbserial1d1140", font.unscii_fantasy)
d.connect()

while True:
    d.write_first_line(time.strftime("%H:%M:%S"), column = 4)
    d.write_second_line(time.strftime("%a %d %b %Y"), column = 0)
    d.send()

