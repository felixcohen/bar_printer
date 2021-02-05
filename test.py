#!/usr/bin/python
from escpos import printer
import forecastio
import requests
import histopy
import datetime
import random
import math
from collections import defaultdict
import RPi.GPIO as GPIO

p = printer.Network("192.168.1.11")
p.image("ec_square.png")
p.set(align=u'center', font=u'a', text_type=u'b',)
p.text(datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")+"\n")
p.text("\n")