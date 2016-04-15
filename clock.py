from hanover_flipdot import display
from hanover_flipdot import fonts
import time

display = display.Display("/dev/ttyUSB0", fonts.unscii_mcr, 128, 16, False, False)

while True:
    display.write_first_line(time.strftime("%H:%M:%S"), column = 32)
    display.write_second_line(time.strftime("%a %d %b %Y"), column = 4)
    display.send()
    time.sleep(1)

