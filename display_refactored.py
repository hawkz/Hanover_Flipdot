#!/usr/bin/python

HEADER = '\x02'
FOOTER = '\x03'

class Output2Display(object):
    "Output to the display over serial connection"
    def __init__(self, port=None, baudrate=4800):
        import serial
        self.serial = serial.Serial(port, baudrate)

    def write(self, data):
        "Write data to serial port"
        self.serial.write(data)


def chr_to_hex_to_4bit(character):
    "Convert the character from hex to number to 4 bit binary string."
    number = int(character, 16)
    binary = bin(number)[2::].zfill(4)
    return binary


def decode_2_bytes_to_number(one, two):
    "Convert the havana encoded two bytes to a number."
    one = chr_to_hex_to_4bit(one)
    two = chr_to_hex_to_4bit(two)
    number = int(one+two, 2)
    return number

def encode_number_to_2_bytes(number):
    "Convert number to havana encoded two bytes"
    binary = bin(number)[2::].zfill(8)
    one = hex(int(binary[:4], 2))[2:].upper()
    two = hex(int(binary[4:], 2))[2:].upper()
    return one, two

def calculate_checksum(data, header, head):
    "Calculate checksum"
    summed = 0
    tmp = [ord(head)]
    for entry in header:
        tmp.append(ord(entry))

    summed += sum(tmp)

    tmp = list()
    for number in data:
        for value in encode_number_to_2_bytes(number):
            tmp.append(ord(value))

    summed += sum(tmp)
    summed += 1

    summed = summed & 0xFF # Chop of everything that falls outside a byte
    summed = summed ^ 255 # XOR it
    summed += 1
    return summed


class OutputSerial(object):
    "Hook into the serial protocol"
    HEADER_LENGTH = 4
    FOOTER_LENGTH = 2
    ROWS = 16
    COLUMNS = None
    ADDRESS = None


    def __init__(self):
        self.header = list()
        self.footer = list()
        self.worker = self.fsm_data
        self.buffer = None # 1 byte buffer
        self.hindex = 0
        self.vindex = 0
        self.data = list()

    def fsm_head(self, character):
        # FSM, handle header
        self.header.append(character)
        if len(self.header) == self.HEADER_LENGTH:
            # When we got the full header we can now calculate the size.
            self.ADDRESS = decode_2_bytes_to_number('0', self.header[1])
            constant = decode_2_bytes_to_number('0', self.header[0])
            number = decode_2_bytes_to_number(self.header[2], self.header[3])
            self.COLUMNS = (number * 8) / self.ROWS
            self.worker = self.fsm_data
            print('#'*self.COLUMNS)
            print('# Header  : ' + str(self.header))
            print('#'*self.COLUMNS)
            print('# Constant: ' + str(constant))
            print('# Address : ' + str(self.ADDRESS))
            print('# Rows    : ' + str(self.ROWS))
            print('# Columns : ' + str(self.COLUMNS))
            print('#'*self.COLUMNS)


    def fsm_foot(self, character):
        # FSM, handle footer
        self.footer.append(character)
        if len(self.footer) == self.FOOTER_LENGTH:
            print('# Footer  : ' + str(self.footer))
            print('# Checksum: ' + str(decode_2_bytes_to_number(*self.footer)))
            calculated = calculate_checksum(self.data, self.header, HEADER)
            print('# Rehashed: ' + str(calculated))

            self.worker = self.fsm_done
            self.worker('')

    def fsm_work(self, character):
        # Handle the character
        self.data.append(decode_2_bytes_to_number(self.buffer, character))

    def fsm_data(self, character):
        # FSM, handle data
        if self.buffer is None:
            self.buffer = character
        else:
            self.fsm_work(character)
            self.buffer = None

    def fsm_done(self, character):
        # FSM, handle done
        print('# Data    : ' + str(len(self.data)))
        print('#'*self.COLUMNS)

        tmp = list()
        while len(tmp) < self.ROWS:
            tmp.append([])

        first = None
        for entry in self.data:
            if first is None:
                first = entry
            else:
                one = bin(entry)[2::].zfill(8)
                two = bin(first)[2::].zfill(8)
                txt = one+two
                txt = txt.replace('0', '-')
                txt = txt.replace('1', '#')
                txt = txt[::-1]
                for index, character in enumerate(txt):
                    tmp[index].append(character)
                first = None

        for row in tmp:
            pass
            print(''.join(row))
        print('#'*self.COLUMNS)


    def write(self, character):
        if character == HEADER:
            self.worker = self.fsm_head
        elif character == FOOTER:
            self.worker = self.fsm_foot
        else:
            self.worker(character)


def encode(matrix_hash_dash, address=1):
    "Encode the matix into Hanover display serial protocol"
    matrix = matrix_hash_dash.split('\n')
    constant = 1
    rows = len(matrix)
    columns = len(matrix[0])
    for column in matrix:
        if len(column) != columns:
            raise ValueError('Matrix not well formed.')

    header = [str(constant),
              str(address)]
    data_size = (rows*columns) / 8
    for character in encode_number_to_2_bytes(data_size):
        header.append(character)

    data = list()
    for index_column in range(columns):
        column = list()
        for index_row in range(rows):
            column.append(matrix[index_row][index_column])

        column = ''.join(column)
        column = column.replace(' ', '0')
        column = column.replace('-', '0')
        column = column.replace('#', '1')

        column = column[::-1]

        nibble_c = column[:4]
        nibble_d = column[4:8]
        nibble_a = column[8:12]
        nibble_b = column[12:]
        for nibble in [nibble_a, nibble_b, nibble_c, nibble_d]:
            number = int(nibble, 2)
            string = hex(number)[2:].upper()
            data.append(string)

    checksum_data = list()
    zipped = zip(data[::2], data[1::2])
    for item in zipped:
        number = decode_2_bytes_to_number(*item)
        checksum_data.append(number)

    footer = calculate_checksum(checksum_data, header, HEADER)
    footer = encode_number_to_2_bytes(footer)

    returns = [HEADER] + header[::] + data + [FOOTER] + list(footer)
    returns = ''.join(returns)

    return returns


def main(matrix, address=1, console_display=False):
    if console_display:
        output = OutputSerial()
    else:
        output = Output2Display('/dev/ttyUSB0')

    encoded = encode(matrix, address)
    for character in encoded:
        output.write(character)


TMP = """
------------------------------------------------------------------------------------------------
--######---##------------------------------------###-###----------######---##-------------------
--##-------##------###---------------------------#######----------##-------##------###----------
--##-------##------------#######-#######-##---##-##-#-##-#######--##-------##------------#######
-#####-----##------##----##---##-##---##-###--##-##---##-##------#####----###------##----##---##
-###-------###-----###---##---##-##---##-###--##-###--##-###-----###------###------###---##---##
-###-------###-----###---#######-#######-#######-###--##-###-----###------###------###---#######
-###-------###-----###---###-----###----------##-###--##-#######-###------######---###---###----
-------------------------###-----###-----#######-----------------------------------------###----
------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------
"""

if __name__ == '__main__':
    from glyphs import five, ten
    from flip import *
    import time

    while True:

	container = list()
	for row in glify('Hey tuesday'.upper() + ' '*13 + str(time.strftime("%H:%M")), five):
	    tmp = list()
	    for item in row:
	        tmp.append(str(int(item)))

	    tmp = ''.join(tmp).ljust(96, '0')
	    tmp += '\n'
	    container.append(''.join(tmp))

	container.append(('0'*96) + '\n')

	for row in glify('Lets Dance!'.upper(), ten):
	    tmp = list()
	    for item in row:
	        tmp.append(str(int(item)))

	    tmp = ''.join(tmp).ljust(96, '0')
	    tmp += '\n'
	    container.append(''.join(tmp))


	while len(container) < 16:
	    container.append(('0'*96) + '\n')

	print(container)

	container = ''.join(container)
	container = container.replace('0', '-')
	container = container.replace('1', '#')

        data = container.strip()
        main(data)

        time.sleep(3)



