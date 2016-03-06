# Python driver for Flipdot destination signs

I recently found an old flipdot bus sign of Hanover brand, and I tried to understand how to control it via my computer.
After some hours of researches, I've finally found how it works.

This python library is the results of my researches and experiments. This kind of displays is hard to find and this library will maybe used only by me :smile:

# Technical info about the display

My display has 128x16 dots. This lib currently works only with this resolution. In the future, I'll maybe change it to support other resolutions.

The display uses a RS-485 bus. I use cheap USB to RS485 converters, like [this one](http://www.amazon.fr/RS485-Convertisseur-Adaptateur-Support-Vista/dp/B00GWEGZOI/ref=sr_1_5?ie=UTF8&qid=1457268055&sr=8-5&keywords=usb+rs485). It does the job very well, and works perfectly on OSX and Linux. (never tested on Windows ...)
