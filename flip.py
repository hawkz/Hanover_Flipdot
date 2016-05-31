#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import numpy as np
import time
from glyphs import five, ten
from flask import Flask


app = Flask(__name__)
np.set_printoptions(threshold='nan', linewidth=200)
MAXWIDTH = 96
MAXHEIGHT = 16
flippy = np.zeros((MAXHEIGHT, MAXWIDTH), dtype=np.int)
os.environ['TZ'] = 'Europe/London'


def erase(flippy):
    """ Reset display to zeros. """
    flippy = np.zeros((MAXHEIGHT, MAXWIDTH), dtype=np.int)
    return flippy


def glify(text, font=five):
    output = np.array([])

    for char in text.replace("", " ")[1:-1]:
        if output.size:
            output = np.hstack((output, np.array(font[char])))
        else:
            output = np.array(font[char])

    return output


def tiny(text):
    """ Set text in 5px font. """
    dots = glify(text.upper().strip(), five)
    return dots


def huge(text):
    """ Set text in 10px font. """
    dots = glify(text.upper().strip(), ten)
    return dots


def place(flippy, dots, pos, reverse=False):
    """ Place dots on display at pos e.g. (2,3). Negative indices allowed. """
    x = pos[0]
    y = pos[1]
    startx = 0
    starty = 0

    if reverse:
        if x < 0:
            x = flippy.shape[1] - dots.shape[1]
        if y < 0:
            y = flippy.shape[0] - dots.shape[0]

        dots = dots[MAXHEIGHT * -1 - y:, MAXWIDTH * -1 - x:]

        # place on flippy
        flippy[y:y + dots.shape[0],
               x:x + dots.shape[1]] = dots

    else:

        if x < 0:
            startx = -1 * x
            x = 0

        if y < 0:
            starty = -1 * y
            y = 0

        # crop to fit
        dots = dots[starty:, startx:]
        dots = dots[0:MAXHEIGHT-y, 0:MAXWIDTH-x]

        # place on flippy
        flippy[y:y + dots.shape[0],
               x:x + dots.shape[1]] = dots

    return flippy


def fliplr(a):
    """ Flip array left to right. """
    return np.fliplr(a)


def flipud(a):
    """ Flip array top to bottom. """
    return np.flipud(a)


def clock():
    """ Output the dots for time. """
    return glify(time.strftime(" %l:%M"))


def convert(flippy):
    """ Convert to Martin's format. """
    for char in ('[ ]'):
        flippy = str(flippy).replace(char, '')
    flippy = flippy.replace('0', '-').replace('1', '#')
    return flippy


@app.route('/topic/<text>')
def topic(text, f=flippy):
    f = place(f, np.zeros((5, 96), dtype=np.int), (0, 0))
    f = place(f, tiny(text), (0, 0))
    display_refactored.main(convert(f))
    return text


@app.route('/say/<text>')
def say(text, f=flippy):
    f = place(f, np.zeros((10, 96), dtype=np.int), (0, 6))
    f = place(f, huge(text), (0, 6))
    display_refactored.main(convert(f))
    return text


@app.route('/raw/<text>')
def raw(text):
    print(text)
    text = text.replace(' ', '')
    display_refactored.main(text)
    return text


@app.route('/clock/')
def tick(f=flippy):
    f = place(f, clock(), (-1, 0), True)
    display_refactored.main(convert(f))
    return 'ok'


@app.route('/clear/')
def clear(f=flippy):
    f = erase(f)
    display_refactored.main(convert(f))
    return 'ok'


if __name__ == '__main__':
    import display_refactored
    app.run(host='::', port=80, debug=True)


