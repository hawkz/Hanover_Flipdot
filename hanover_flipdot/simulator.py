#/usr/bin/python

class Simulator(object):
    def __init__(self):
        print "\033[2J"

    def display(self, frame):
        # Parse each column
        for i in range(len(frame)/4):
            # There's two time 16 bits
            for j in range(2):
                # Grab the two bytes
                b1 = frame[(2*j)+(i*4)]
                b2 = frame[(2*j)+((i*4)+1)]
                # Combine two ASCII bytes into one hex byte
                if b1 > 0x40:
                    b1 -= 0x37
                else:
                    b1 -= 0x30
                if b2 > 0x40:
                    b2 -= 0x37
                else:
                    b2 -= 0x30
                byte = ((b1 * 16) + b2)

                for k in range(7, -1, -1):
                    if byte & (1 << (k)):
                        print "\033[%d;%dH0"%((8*j)+k+3, i+2)
                    else:
                        print "\033[%d;%dH "%((8*j)+k+3, i+2)
