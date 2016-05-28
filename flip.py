#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import time
import numpy as np
from glyphs import five, ten


show_clock = True
flippy = np.zeros((96, 16), dtype=np.int)
os.environ['TZ'] = 'Europe/London'


def glify(text, font=ten):
    if font == ten:
        output = np.array([[], [], [], [], [], [], [], [], [], []], dtype=np.int)
    elif font == five:
        output = np.array([[], [], [], [], []], dtype=np.int)

    for char in text.replace("", " ")[1:-1]:
        output = np.concatenate((output, np.array(font[char])), axis=1)

    return output


def tiny(text):
    """ Set text in 5px font. """
    dots = glify(text, five)
    return dots


def huge(text):
    """ Set text in 10px font. """
    dots = glify(text, ten)
    return dots


def place(dots, pos):
    """ Place dots on display at pos e.g. (2,3) or (-1,3) for right aligned. """
    dots = np.array(dots)
    x = pos[0]
    y = pos[1]
    flippy[y:y+dots.shape[0],
           x:x+dots.shape[1]] = dots


def clock():
    """ Output the dots for time. """
    return glify(time.strftime("%l:%M").strip())
