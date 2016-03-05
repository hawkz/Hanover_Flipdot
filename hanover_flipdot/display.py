#!/usr/bin/python

import serial
import time
import sys
from simulator import *

class Display(object):
    '''
    Driver for the Hanover display.
    Currently, this driver only works with resolution of 128x16, at address 1
    This limitation must be changed in a future version.
    '''
    def __init__(self, serial, font, debug=False, simulator=False):
        self.port = serial
        # Header part
        self.header = [0x2, 0x31, 0x31, 0x30, 0x30]
        # Footer part
        self.footer = [0x3, 0x00, 0x00]
        # Data buffer
        self.buf = [0x30] * 512
        # Font buffer
        self.font = font
        # Debug flag
        self.DEBUG = debug
        # Simulator switch
        self.SIMULATOR = simulator
        if self.SIMULATOR:
            self.sim = Simulator()

        self.connect()

    def connect(self):
        '''
        Connect to the serial device
        '''
        if not self.SIMULATOR:
            try:
                self.ser = serial.Serial(port=self.port, baudrate=4800)
            except:
                print sys.exc_info()
                print "Error opening serial port"
                self.ser = None
            if self.DEBUG:
                print "Serial port:", self.ser
        elif self.DEBUG:
            print "Simulator instance", self.sim


    def set_font(self, font):
        '''
        Set a font
        '''
        self.font = font

    def erase_first_line(self):
        '''
        Erase the first line
        '''
        if self.DEBUG:
            print "Erasing first line"
        write_first_line("                ")

    def erase_second_line(self):
        '''
        Erase the second line
        '''
        if self.DEBUG:
            print "Erasing second line"
        write_second_line("                ")

    def erase_all(self):
        '''
        Erase all the screen
        '''
        if self.DEBUG:
            print "Erasing all"
        for i in range(512):
            self.buf[i] = 0x30

    def write_first_line(self, text, column=0):
        '''
        Write text on the first line
        '''
        # Check for length integrity
        if len(text) > 16:
            return -1

        if self.DEBUG:
            print "First line text :  ", text

        # Parse all the characters
        for char in text:
            idx = 0
            byte = 0
            # Fill the buffer
            for i in range(8):
                self.buf[(column * 32)+(byte)] = (self.font[ord(char)][idx])
                byte += 1
                self.buf[(column * 32)+(byte)] = (self.font[ord(char)][idx+1])
                byte += 3
                idx+= 2
            column += 1

    def write_second_line(self, text, column=0):
        '''
        Write text on the second line
        '''
        if len(text) > 16:
            return -1

        if self.DEBUG:
            print "Second line text : ", text

        for char in text:
            idx = 0
            # Drop the two first bytes
            byte = 2
            for i in range(8):
                self.buf[(column*32)+(byte)] = (self.font[ord(char)][idx])
                byte += 1
                self.buf[(column*32)+(byte)] = (self.font[ord(char)][idx+1])
                byte += 3
                idx+= 2
            column += 1

    def write_center(self, text, column=0):
        '''
        Write text on the center of the screen
        '''
        if len(text) > 16:
            return -1

        if self.DEBUG:
            print "Center line text : ", text

        for char in text:
            idx = 0
            byte = 0
            for i in range(8):
                self.buf[(column*32)+(byte)] = (self.font[ord(char)][idx+1])
                byte += 1
                self.buf[(column*32)+(byte)] = 0x30
                byte += 1
                self.buf[(column*32)+(byte)] = 0x30
                byte += 1
                self.buf[(column*32)+(byte)] = (self.font[ord(char)][idx])
                byte += 1
                idx+= 2
            column += 1

    def byte_to_ascii(self, byte):
        '''
        Convert a byte to its ascii reprensentation.
        The transmission represent each byte by their ASCII representation.
        For example, 0x67 is reprensented by 0x36 0x37 (ascii 6 and ascii 7)
        This is not an elegant way to convert the data, and this function must
        be refactored
        '''
        b1 = 0
        b2 = 0
        if (byte >> 4) > 9:
            b1 += 0x37
        else:
            b1 += 0x30

        if (byte % 16) > 9:
            b2 += 0x37
        else:
            b2 += 0x30

        return (b1, b2)

    def __checksum__(self):
        '''
        Compute the checksum of the data frame
        '''
        sum = 0
        # Sum all bytes of the header and the buffer
        for byte in self.header:
            sum += byte
        for byte in self.buf:
            sum += byte

        # Start of text (0x02) must be removed,
        # End of text (0x03) must be added
        sum += 1

        # Result must be casted to 8 bits
        sum = sum & 0xFF

        # Checksum is the sum XOR 255 + 1. So, sum of all bytes + checksum
        # is equal to 0 (8 bits)
        crc =  (sum ^ 255) + 1

        # Transfor the checksum in ascii
        crc1, crc2 = self.byte_to_ascii(crc)

        # Add the checksum on the footer
        self.footer[1] = crc1
        self.footer[2] = crc2

        if self.DEBUG:
            print "SUM : %d, CRC : %d, SUM + CRC : %d"%(sum, crc, sum+crc)

    def send(self):
        '''
        Send the frame via the serial port
        :return: Return 0 on success, -1 on errors
        '''
        # Compute the checksum
        self.__checksum__()

        if self.DEBUG:
            print self.header, self.buf, self.footer
            print ""
        if not self.SIMULATOR:
            try:
                # Send the header
                for byte in self.header:
                    self.ser.write(chr(byte))
                # Send the data
                for byte in self.buf:
                    self.ser.write(chr(byte))
                # Send the footer
                for byte in self.footer:
                    self.ser.write(chr(byte))

                return 0
            except:
                return -1
        else:
            self.sim.display(self.buf)
            return 0
