#/usr/bin/python

class Simulator(object):
    def __init__(self):
        print "\033[2J"

    def __unascii__(self, byte):
        if byte > 0x40:
            return byte - 0x37
        else:
            return byte - 0x30

    def display(self, frame):
        # Parse each column
        for i in range(len(frame)/4):
            b1 = frame[(i*4)+1]
            b2 = frame[(i*4)+0]
            b3 = frame[(i*4)+3]
            b4 = frame[(i*4)+2]
            # Combine the four ASCII bytes into one hex byte
            b1 = self.__unascii__(b1)
            b2 = self.__unascii__(b2)
            b3 = self.__unascii__(b3)
            b4 = self.__unascii__(b4)

            byte = ((b3*4096) + (b4*256) + (b1 * 16) + b2)

            for k in range(15, -1, -1):
                if byte & (1 << (k)):
                    print "\033[43m\033[%d;%dH \033[0m"%((k+1), i)
                else:
                    print "\033[100m\033[%d;%dH \033[0m"%((k+1), i)
