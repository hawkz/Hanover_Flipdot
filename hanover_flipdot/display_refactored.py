#!/usr/bin/python

import fonts

class Output2Display(object):
    "Output to the display over serial connection"
    def __init__(self, port=None, baudrate=4800):
        import serial
        self.serial = serial.Serial(port, baudrate)
    
    def write(self, data):
        "Write data to serial port"
        self.serial.write(data)


class Output2Console(object):
    "Output to console"
    LEN_HEADER = 5
    LEN_FOOTER = 3
    LEN_COLUMN = 16
    
    def __init__(self, mirror=True):
        self.count = 0
        self.data = list()
        self.mirror = mirror
        
        
    def write(self, data):
        "Write to console"
        self.data.append(data)
        if len(self.data) == 520:
            self.process()
        
    def process(self):
        "Process data"
        data = self.data[::] # make a working copy
        
        # Extract Header
        head = data[:self.LEN_HEADER]
        data = data[self.LEN_HEADER:]
        
        # Extract Footer
        foot = data[-self.LEN_FOOTER:]
        data = data[:-self.LEN_FOOTER]

        print('Required terminal width: ' + \
                           str(len(data) * 4 / self.LEN_COLUMN) + ' characters')

        print('Data protocol header: ' + str(head))
        print('Data protocol footer: ' + str(foot))
        
        # We have now 512 bytes left in data.
        # Each byte is an ASCII character (text).
        # Each character can only be one of 0123456789ABCDEF, effectively a very
        # inefficient encoding of hexadecimal. Each character, being hexadecimal
        # encodes 4 binary values vertically.
        
        
        # Iterate over each character, convert it to a number, then to binary
        tmp = list()
        for character in data:
            number = int(character, 16)
            binary = bin(number)[2::].zfill(4)
            tmp.append(binary)
        data = ''.join(tmp)
        
        # Setup an empty matrix with row amount equal to binary_height_column
        tmp = list()
        while len(tmp) < self.LEN_COLUMN:
            tmp.append([])
        
        # Iterate over the binary string, chopping it up in columns
        while len(data) > 0:
            column, data = data[:self.LEN_COLUMN], data[self.LEN_COLUMN:]
            
            # iterate over the column and append each 'bit' to the corresponding
            # row
            for index, bit in enumerate(column):
                if bit == '0':
                    appendix = '-'
                elif bit == '1':
                    appendix = '#'
                tmp[index].append(appendix)
        
        if self.mirror:
            # Flip the rows vertically
            tmp = tmp[::-1]
            
        for row in tmp: 
            print(''.join(row)) 
        


class Display(object):
    '''
    Driver for the Hanover display.
    Currently, this driver only works with resolution of 128x16, at address 1
    This limitation must be changed in a future version.
    '''
    def __init__(self, address, columns, lines, font):
        if lines % 8:
            lines = lines + (8-(lines % 8))

        self.columns = columns - 1

        self.data = ((lines * columns) / 8)

        res1, res2 = self.byte_to_ascii(self.data & 0xff)

        self.byte_per_column = lines / 8

        address += 16
        
        add1, add2 = self.byte_to_ascii(address)
        # Header part
        self.header = [0x2, add1, add2, res1, res2]
        # Footer part
        self.footer = [0x3, 0x00, 0x00]
        # Data buffer initialized to 0
        self.buf = [0] * (self.data / self.byte_per_column)
        # Fonts object
        self.font = font

    def connect(self, output):
        '''
        Connect to the serial device
        '''
        self.ser = output

    def set_font(self, font):
        '''
        Set a font
        '''
        self.font = font

    def erase_all(self):
        '''
        Erase all the screen
        '''
        for i in range(len(self.buf)):
            self.buf[i] = 0

    def write_text(self, text, line=0, column=0):
        '''
        Write text on the first line
        '''
        # Detect the size
        mask = 0xff
        for byte in self.font[0x31]:
             if byte.bit_length >= 9:
                mask = 0xffff
                break

        # Parse all the characters
        for char in text:
            # Fill the buffer
            for i in range(len(self.font[0])):
                if column > self.columns:
                    return 0
                self.buf[column] &= ~((mask << line) & (1 << (self.byte_per_column * 8))) -1
                self.buf[column] |= ((self.font[ord(char)][i])<<line) &  (1 << (self.byte_per_column * 8)) - 1
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
        b1 = byte >> 4
        if b1 > 9:
            b1 += 0x37
        else:
            b1 += 0x30

        b2 = byte % 16
        if b2 > 9:
            b2 += 0x37
        else:
            b2 += 0x30

        return (b1, b2)

    def __checksum__(self, dsum):
        '''
        Compute the checksum of the data frame
        '''
        sum = 0
        # Sum all bytes of the header and the buffer
        for byte in self.header:
            sum += byte
        
        sum += dsum

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


    def send(self):
        '''
        Send the frame via the serial port
        :return: Return 0 on success, -1 on errors
        '''

        crc = 0
        try:
            # Send the header
            for byte in self.header:
                self.ser.write(chr(byte))
            # Send the data
            for col in self.buf:
                for i in range(self.byte_per_column):
                    b1, b2 = self.byte_to_ascii((col >> (8*i) & 0xFF))
                    crc += b1
                    crc += b2
                    self.ser.write(chr(b1))
                    self.ser.write(chr(b2))
    
            # Compute the checksum
            self.__checksum__(crc)

            # Send the footer
            for byte in self.footer:
                self.ser.write(chr(byte))

            return 0
        except:
            return -1


def main(text, console_display=False):
    display = Display(1, 128, 16, fonts.unscii_mcr)
    
    if console_display:
        output = Output2Console()
    else:
        output = Output2Display()
        
    display.connect(output)
    
    display.write_text(text)
    display.send()


if __name__ == '__main__':
    main('FlippyMcFlip', console_display=True)
    
    
