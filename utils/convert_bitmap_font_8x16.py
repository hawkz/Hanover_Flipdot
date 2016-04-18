#!/usr/bin/python
import sys

# Check for argument
if len(sys.argv) != 3:
    print "Usage : python convert_bitmap_font.py font.hex font_name"
    sys.exit(1)

filename = sys.argv[1]
fontname = sys.argv[2]
f = open(filename)
fonts = []

# Read the font from 0x32 (space) to 0x7F (DEL)
for line in range(0x7F):
    fonts.append(int(f.readline().split(":")[1].rstrip("\n"), base=16))

# Create a buffer for the final font
final_font = []

# Parse each characters
for char in fonts:
    # Decompose the character byte by byte
    original_char = [0x00] * 16
    # Read the char byte by byte, and reorder it
    for i in range(16):
        original_char[i] = (char >> (120-(8*(i)))) & 0xFF

    hanover_char = [0x0000] * 8 

    # Convert from line by line font to column by column
    k = 15
    for i in range(8): # Column
        for j in range(16): # line
            hanover_char[i] |= ((original_char[j] >> (7-i)) & 1) << j 
        k -= 1

    # Put the char in the final buffer
    final_font.append(hanover_char)

print fontname + " = ["
for char in final_font:
    print "     [%#.4x, %#.4x, %#.4x, %#.4x, %#.4x, %#.4x, %#.4x, %#.4x],"\
    %(char[0], char[1], char[2], char[3], char[4], char[5], char[6], char[7])
print "]"
print ""
