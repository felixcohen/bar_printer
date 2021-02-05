import sys
import evdev
import spotipy
import spotipy.util as util
from escpos import printer
import forecastio
import requests
import histopy
import datetime
import random
import math
import urllib2
from collections import defaultdict

api_key = "DARK SKY API KEY HERE"
lat = 51.5461738
lng = -0.0567503
forecast = forecastio.load_forecast(api_key, lat, lng)

tfl = TfLBusArrivalsAPI()

def fetchBusArrivals(bSC):

  try:
    jsonObject = tfl.returnTfLJSON(bus_stop_code=bSC)
  except urllib.error.URLError:
    print("Unable to connect to Internet...")


  busLineDestinationTime = []

  for entry in jsonObject:
    bLDT = []
    bLDT.append(entry['lineName'])
    bLDT.append(entry['destinationName'])
    bLDT.append(int(entry['timeToStation'])/60.0)
    busLineDestinationTime.append(bLDT)

  arrivalsList = sorted(busLineDestinationTime, key=lambda x:x[2])
  arrivalsList = arrivalsList[0:6]
  return arrivalsList

def refresh_token(spotify):
    cached_token = spotify.get_cached_token()
    refreshed_token = cached_token['refresh_token']
    new_token = spotify.refresh_access_token(refreshed_token)
    # also we need to specifically pass `auth=new_token['access_token']`
    spotify = spotipy.Spotify(auth=new_token['access_token'])
    return new_token

scope = 'user-read-currently-playing'
username = "SPOTIFY USER NAME HERE"
current_song = ""
hour = ""

token = util.prompt_for_user_token(username,scope,client_id='SPOTIFY APP ID',client_secret='SPOTIFY APP SECRET',redirect_uri='http://localhost:5000/callback')
sp = spotipy.Spotify(auth=token)


p = printer.Network("PRINTER STATIC IP")

TRIGGER_DEVICE = 'AB Shutter3'

def get_BT_device_list():
    devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]

    # failure if devices list empty
    if len(devices) == 0:
        print("No devices found, try running with sudo")
        sys.exit(1)

    # iteratively check device list for BT device
    print('checking connected devices...')
    for device in devices:
        if device.name == TRIGGER_DEVICE: # look for trigger device
            print(device)
            device.grab() # other apps unable to receive events until device released
            for event in device.read_loop():
                if event.type == evdev.ecodes.EV_KEY:
                    data = evdev.categorize(event)  # Save the event temporarily to introspect it
                    if data.keystate == 1:  # Down events only
                        print(data.scancode)
                        if data.scancode == 28:
                          p = printer.Network("192.168.1.30")
                          p.image("ec_square.png")
                          p.set(align=u'center', font=u'a', text_type=u'b',)
                          p.text(datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")+"\n")
                          results = sp.current_user_playing_track()
                          result = results['item']
                          artist = result['artists'][0]['name']
                          title = result['name']
                          song = artist+"-"+title
                          p.text(song+"\n")
                          p.cut()
                        if data.scancode == 115:
                          p = printer.Network("192.168.1.30")
                          p.image("ec_square.png")
                          p.set(align=u'center', font=u'a', text_type=u'b',)
                          p.text(datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")+"\n")
                          byMinute = forecast.minutely()
                          p.text(byMinute.summary)
                          p.text("\n")
                          today = datetime.datetime.now()
                          p.set(align=u'left', font=u'b', text_type=u'normal',)
                          #today_in_history = histopy.load_history(today)
                          #events = histopy.load_events(today_in_history)
                          #random_year = random.choice(list(events))
                          #event = events[random_year]
                          #p.text(word_wrap('\nOn this day in '+random_year+', '+event+'\n'))

                          locations = ["HACKNEY TOWN HALL","MORNING LANE / TRELAWNEY ESTATE", "HACKNEY CENTRAL OVERGROUND"]

                          for location in locations:
                            print location
                            p.set(align=u'center', font=u'b', text_type=u'b',)
                            p.text("\n")
                            p.text(location.title()+"\n")
                            this_stop=tfl.searchBusStop(location)
                            this_stop_code = this_stop[location]

                            buses = fetchBusArrivals(this_stop_code)
                            p.set(align=u'center', font=u'b', text_type=u'normal',)
                            for bus in buses:
                              bus_no = bus[0]
                              bus_destination = bus[1]
                              bus_mins_to_arrival = "in %s min " % (bus[2])
                              line1 = "to "+ bus_destination
                              if bus[2] > 200:
                                bus_mins_to_arrival = "* "
                                line1 = "Station closed *"
                              p.text(bus_mins_to_arrival)
                            for bus, times in buses.items():
                              if (times[0] > 120):
                                p.text("Station closed")
                              else:
                                print_times = ""
                                sorted_times = sorted(times)
                                for time in sorted_times:
                                   print_times = print_times+str(time)+","
                                print_times = print_times[:-1]
                                p.text("%s in %s minutes\n" % (bus, print_times))
                          p.set(align=u'center', font=u'a', text_type=u'normal',)
                          p.text("\nOur postcode is ")
                          p.set(align=u'center', font=u'a', text_type=u'b',)
                          p.text("E9 6ND\n")
                          p.set(align=u'center', font=u'a', text_type=u'normal',)
                          p.text("Mare St Cars: 020 8986 4211\n\n") 
                          p.text("Thanks for joining us at Every Cloud")
                          p.cut()
                          p.close()
if __name__ == "__main__":
    get_BT_device_list();