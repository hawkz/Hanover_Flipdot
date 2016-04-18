from hanover_flipdot import display
from hanover_flipdot import fonts
import time

display = display.Display("/dev/ttyUSB0", fonts.unscii_mcr, 128, 16, False, True)

while True:
    display.write_text(time.strftime("%H:%M:%S"), line = 0, column = 4)
    display.write_text(time.strftime("%a %d %b %Y"), line = 8, column = 0)
    display.send()
    time.sleep(1)

