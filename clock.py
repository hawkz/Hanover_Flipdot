from hanover_flipdot import display
from hanover_flipdot import fonts
import time

display = display.Display("/dev/tty.wchusbserial1a1230", 5, 144, 19, fonts.unscii_mcr, True, False)

while True:
    display.write_text(time.strftime("%H:%M:%S"), line = 3, column = 40)
    display.write_text(time.strftime("%a %d %b %Y"), line = 11, column = 8)
    display.send()
    time.sleep(.3)

