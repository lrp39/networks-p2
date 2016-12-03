import socket
import urllib2
import json
from math import radians, cos, sin, atan2,sqrt,fabs

vm_ip = '129.22.146.171' #hard coded in ip address of the machine this is tested on

def get_coordinates(ip_address):
	#answer from: http://stackoverflow.com/questions/645312/what-is-the-quickest-way-to-http-get-in-python
	response = urllib2.urlopen("http://freegeoip.net/json/"+ ip_address).read()
	results = json.loads(response)
	return results["latitude"], results["longitude"]

#get coodinates of self
vm_lat, vm_long = get_coordinates(vm_ip)
vm_lat_radians = radians(vm_lat)
vm_long_radians = radians(vm_long)

# Get list of target sites
with open("targets.txt") as file:
        targets = file.read().splitlines()
file.close()

for target in targets:
	#get coordinates in radians
	target_lat,target_long = get_coordinates(socket.gethostbyname(target))	
	target_lat_radians = radians(target_lat)
	target_long_radians =radians(target_long)
	
	#answer from http://stackoverflow.com/questions/27928/calculate-distance-between-two-latitude-longitude-points-haversine-formula
	dlat=(vm_lat_radians - target_lat_radians)
	dlong=(vm_long_radians - target_long_radians)
	a = sin(dlat/2)**2 + (cos(vm_lat_radians) * cos(target_lat_radians) * sin(dlong/2)**2)
	c= 2 * atan2(sqrt(a), sqrt(1-a))
	r = 6371 #radius of earth in km
	d = r *c 
	print 'Distance for ' + target + 'is ' + str(d) + ' km'
