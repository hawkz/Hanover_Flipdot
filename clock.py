from hanover_flipdot import display
from hanover_flipdot import fonts
import time

display = display.Display("/dev/ttyUSB0", 1, 96, 16, fonts.unscii_mcr, True, False)

while True:
    display.erase_all()
    display.send()
    display.write_text(time.strftime("%H:%M:%S"), line = 1, column = 1)
#    display.write_text(time.strftime("%a %d %b %Y"), line = 11, column = 8)
    display.send()
    time.sleep(3)

