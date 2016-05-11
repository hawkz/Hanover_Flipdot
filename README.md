# Python driver for Flipdot destination signs

This library is a quick (and dirty) python implementation of the protocol used for the Hanover's displays. 

This library is able to send text (and, for now, only text) to the display. In the future, I plan to improve the library with plotting functions.

Theoretically, it is capable to drive any display whatever the resolution, althought only a few number of resolutions have actually been tested.


# Prerequisties

These displays communicates through a RS-485 bus. To use these display, a RS-485 converter is required. Personnaly, I use a cheap USB to RS485 converter, like [this one](http://www.amazon.fr/RS485-Convertisseur-Adaptateur-Support-Vista/dp/B00GWEGZOI/ref=sr_1_5?ie=UTF8&qid=1457268055&sr=8-5&keywords=usb+rs485). It does the job very well, and works perfectly on OSX and Linux. (never tested on Windows thought...)

# The protocol explained

All the data sent to the displays are in an ASCII representation, meaning that each bytes (or, pratically, 8 dots) are represented by two ASCII bytes. For example, ```0x3E``` will be represented by following ASCII sequence : ```0x33 0x45```. 

The data bytes are treated column by column, from the upper-left corner to the lower-right corner. The amount of data sent for a resolution of 128x16 for example will be ```((128 * 16 * 2) / 8)``` bytes.

The data are preceded by a header with the following format :

```[START OF TEXT][ADDRESS][RESOLUTION]```.

- ```START OF TEXT``` is always equal to 0x02 (ASCII SOT code)
- ```ADDRESS``` is coded with two ASCII byte. For an unknown reason, the MSB part is always equal to 0x31 (1). The LSB part is equal to the address defined by the rotary switch located inside the display + 1.
- ```RESOLUTION``` is the number of data bytes that will be sent. This value is computed that way : ```width * height / 8```

The following sequence shows the header for a 128x16 display with address 1 : ```0x02 0x31 0x31 0x30 0x30``

The data are followed by a footer and a checksum :

```[END OF TEXT][CHECKSUM]```

- ```END OF TEXT``` is always equal to 0x03 (ASCII EOT code)
- ```CHECKSUM``` is ```(sum of all data bytes + all header bytes + EOT - SOT ^ 255) + 1```

For example, here's a complete frame for a 21*16 display :

```
0x02 0x31 0x33 0x32 0x41                                # Header
0x30 0x30 0x30 0x30 0x30 0x38 0x30 0x36 0x46 0x43 0x30  # Data
0x37 0x46 0x43 0x30 0x37 0x30 0x30 0x30 0x36 0x30 0x30  # ...
0x30 0x30 0x46 0x38 0x30 0x33 0x46 0x43 0x30 0x37 0x30  # ...
0x43 0x30 0x36 0x30 0x43 0x30 0x36 0x46 0x43 0x30 0x37  # ...
0x46 0x38 0x30 0x33 0x30 0x30 0x30 0x30 0x46 0x38 0x30  # ...
0x33 0x46 0x43 0x30 0x37 0x30 0x43 0x30 0x36 0x30 0x43  # ...
0x30 0x36 0x46 0x43 0x30 0x37 0x46 0x38 0x30 0x33 0x30  # ...
0x30 0x30 0x30 0x30 0x30 0x30 0x30                      # End of data
0x03 0x34 0x41                                          # Footer
```


