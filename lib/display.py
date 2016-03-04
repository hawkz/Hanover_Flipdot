#!/usr/bin/python

import serial
import time

class Display(object):
    def __init__(self, serial, font):
        self.port = serial
        self.header = [0x2, 0x31, 0x31, 0x30, 0x30] 
        self.footer = [0x3, 0x00, 0x00]
        self.buf = [0x30] * 512
        self.font = font

    def connect(self):
        self.ser = serial.Serial(port=self.port, baudrate=4800)
        print self.ser
        print "Serial port opened"

    def erase(self):
        for i in range(512):
            self.buf[i] = 0x30

    def write_first_line(self, text, column=0):
        count = 512
        if len(text) > 16:
            print "Too long string"
            return -1

        for char in text:
            j = 0
            x = 0
            idx = 0
            for i in range(8):
                self.buf[(column*32)+(idx)] = (self.font[ord(char)][j])
                idx += 1
                self.buf[(column*32)+(idx)] = (self.font[ord(char)][j+1])
                idx += 3
                j+= 2
                count -= 4
            column += 1
    
    def write_second_line(self, text, column=0):
        count = 512
        if len(text) > 16:
            print "Too long string"
            return -1

        for char in text:
            j = 0
            x = 0
            idx = 0
            for i in range(8):
                idx += 2
                self.buf[(column*32)+(idx)] = (self.font[ord(char)][j])
                idx += 1
                self.buf[(column*32)+(idx)] = (self.font[ord(char)][j+1])
                idx += 1
                j+= 2
                count -= 4
            column += 1
        

    def write_center(self, text, column=0):
        count = 512
        if len(text) > 16:
            print "Too long string"
            return -1

        for char in text:
            j = 0
            x = 0
            idx = 0
            for i in range(8):
                self.buf[(column*32)+(idx)] = (self.font[ord(char)][j+1])
                idx += 1
                self.buf[(column*32)+(idx)] = 0x30
                idx += 1
                self.buf[(column*32)+(idx)] = 0x30
                idx += 1
                self.buf[(column*32)+(idx)] = (self.font[ord(char)][j])
                idx += 1
                j+= 2
                count -= 4
            column += 1

    def __crc__(self):
        sum = 0
        for byte in self.header:
            sum += byte

        for byte in self.buf:
            sum += byte

        sum += 3
        sum -= 2
        
        sum = sum & 0xFF

        crc = 256 - sum

        crc1 = crc >> 4
        if crc1 > 9:
            crc1 += 0x37
        else:
            crc1 += 0x30

        crc2 = crc % 16
        if crc2 > 9:
            crc2 += 0x37
        else:  
            crc2 += 0x30

        self.footer[1] = crc1
        self.footer[2] = crc2

    def send(self):
        self.__crc__()

        for byte in self.header:
            self.ser.write(chr(byte))
        for byte in self.buf:
            self.ser.write(chr(byte))
        for byte in self.footer:
            self.ser.write(chr(byte))
