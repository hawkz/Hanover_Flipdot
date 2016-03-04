from fonts import font
import lib.display
import time

display = lib.display.Display("/dev/tty.wchusbserial1d1140", font.unscii_fantasy, True)

while True:
    display.write_first_line(time.strftime("%H:%M:%S"), column = 4)
    display.write_second_line(time.strftime("%a %d %b %Y"), column = 0)
    display.send()
    time.sleep(1)

