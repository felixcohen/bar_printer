#!/usr/bin/python
from escpos import printer
import forecastio
import requests
import histopy
import datetime
import random
import math
from collections import defaultdict


api_key = "0a067220d45ae859429fb6382a92dc89"
lat = 51.5461738
lng = -0.0567503

forecast = forecastio.load_forecast(api_key, lat, lng)

from TfLAPI import *
import time, sys
from multiprocessing import Process

tfl = TfLBusArrivalsAPI()

def word_wrap(string, width=56, ind1=0, ind2=0, prefix=''):
    """ word wrapping function.
        string: the string to wrap
        width: the column number to wrap at
        prefix: prefix each line with this string (goes before any indentation)
        ind1: number of characters to indent the first line
        ind2: number of characters to indent the rest of the lines
    """
    string = prefix + ind1 * " " + string
    newstring = ""
    while len(string) > width:
        # find position of nearest whitespace char to the left of "width"
        marker = width - 1
        while not string[marker].isspace():
            marker = marker - 1

        # remove line from original string and add it to the new string
        newline = string[0:marker] + "\n"
        newstring = newstring + newline
        string = prefix + ind2 * " " + string[marker + 1:]

    return newstring + string

def fetchBusArrivals(bSC):

	try:
		buses = result = defaultdict(list)
		jsonObject = tfl.returnTfLJSON(bus_stop_code=bSC)
		busLineDestinationTime = []

		for entry in jsonObject:
			if entry['lineName'] != "London Overground" and entry['lineName'] != "TfL Rail":
				bus = entry['lineName'] + " - " + entry['destinationName']
			else:
				bus = entry['destinationName'].replace(" Rail Station", "")

			time = int(entry['timeToStation']/60.0)

			if (time > 4):
				if bus in buses:
					buses[bus].append(time)
				else:
					buses[bus] = [time]
				# bLDT = []
				# bLDT.append(entry['lineName'])
				# bLDT.append(entry['destinationName'])
				# bLDT.append(int(entry['timeToStation'])/60.0)
				# busLineDestinationTime.append(bLDT)

		# arrivalsList = sorted(busLineDestinationTime, key=lambda x:x[2])
		# arrivalsList = arrivalsList[0:6]
		return buses
	except urllib2.URLError:
		print("Unable to connect to Internet...")


p = printer.Network("192.168.1.5")
p.image("ec_square.png")
p.set(align=u'center', font=u'a', text_type=u'b',)
p.text(datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")+"\n")
byMinute = forecast.minutely()
p.text(byMinute.summary)
p.text("\n")


today = datetime.datetime.now()
p.set(align=u'left', font=u'b', text_type=u'normal',)
today_in_history = histopy.load_history(today)
events = histopy.load_events(today_in_history)
random_year = random.choice(list(events))
event = events[random_year]
p.text(word_wrap('\nOn this day in '+random_year+', '+event+'\n'))

locations = ["HACKNEY TOWN HALL","MORNING LANE / TRELAWNEY ESTATE", "HACKNEY CENTRAL OVERGROUND"]

for location in locations:
	print location
	p.set(align=u'center', font=u'b', text_type=u'b',)
	p.text("\n")
	p.text(location.title()+"\n")
	# returns a dictionary of stop codes for stops that fit the search criteria, could > 1
	this_stop=tfl.searchBusStop(location)
	# get the code by lookup from the dictionary, if we know the name in advance
	this_stop_code = this_stop[location]
	# we can print this here if we're just searching

	# we'll use out this_stop_code which we looked up as an input
	# it will fail if there is more than one stop returned !
	# get JSON response for this bus stop code each time before we show the buses
	buses = fetchBusArrivals(this_stop_code)
	p.set(align=u'center', font=u'b', text_type=u'normal',)
	# for bus in buses:
		# bus_no = bus[0]
		# bus_destination = bus[1]
		# bus_mins_to_arrival = "in %.0f min " % (bus[2])
		# 	line1 = "to "+ bus_destination
		# 	if bus[2] > 200:
		# 		bus_mins_to_arrival = "* "
		# 		line1 = "Station closed *"
		# p.text(bus_mins_to_arrival)
	for bus, times in buses.items():
		print_times = ""
		sorted_times = sorted(times)
		for time in sorted_times:
		   print_times = print_times+str(time)+","
		print_times = print_times[:-1]
		p.text("%s in %s minutes\n" % (bus, print_times))
		# p.text("\n")
p.set(align=u'center', font=u'a', text_type=u'normal',)
p.text("\nOur postcode is ")
p.set(align=u'center', font=u'a', text_type=u'b',)
p.text("E9 6ND\n")
p.set(align=u'center', font=u'a', text_type=u'normal',)
p.text("Mare St Cars: 020 8986 4211\n\n") 
p.text("Thanks for joining us at Every Cloud")
p.cut()
p.close()
time.sleep(1)
