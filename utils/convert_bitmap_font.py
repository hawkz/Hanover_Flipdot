#!/usr/bin/python
import sys

# Check for argument
if len(sys.argv) != 3:
    print "Usage : python convert_bitmap_font.py font.hex font_name"
    sys.exit(1)

filename = sys.argv[1]
fontname = sys.argv[2
]
f = open(filename)
fonts = []
for line in range(0x100):
    fonts.append(int(f.readline().split(":")[1].rstrip("\n"), base=16))

# Create a buffer for the final font
final_font = []

# Parse each characters
for char in fonts:
    # Decompose the character byte by byte
    original_char = [0x00] * 8
    # Put the sequence in an array
    for i in range(8):
        original_char[i] = (char >> (8*(i))) & 0xFF

    hanover_char = [0x00] * 8

    j = 7
    for byte in original_char:
        for i in range(8):
            hanover_char[(i)] |= ((byte >> (7-i)) & 1) << j
        j -= 1

    final_font.append(hanover_char)


final = []
for font in final_font:
    char = []
    for i in range(8):
        char.append(ord("%X"%(font[i] >> 4)))
        char.append(ord("%X"%(font[i] % 16)))
    
    final.append(char)

print fontname + " = ["
for char in final:
    print "    "+str(char)+","
print "]"
print ""
