from hanover_flipdot import display
from hanover_flipdot import fonts
import time

display = display.Display("/dev/tty.wchusbserial1d1140", fonts.unscii_mcr, 96, 16, False, True)

while True:
    display.write_first_line(time.strftime("%H:%M:%S"), column = 4)
    display.write_second_line(time.strftime("%a %d %b %Y"), column = 0)
    display.send()
    time.sleep(1)

