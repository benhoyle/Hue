import requests
import time
import ConfigParser
import logging
import json
from ast import literal_eval

class lights():		
	def __init__(self):
		parser = ConfigParser.SafeConfigParser()
		parser.read('config.ini')
		self.ip = parser.get('Hue Config', 'ip')
		self.sunset_colour = literal_eval(parser.get('Hue Config', 'sunset_colour'))
		self.user = parser.get('Hue Config', 'user')
		response = requests.get("http://%s/api/%s/lights" % (self.ip, self.user))
		self.lights_dict = response.json()
		self.number = len(self.lights_dict)	
	
	def set_light(self, light, data):
		#logging.error(json.dumps(data))
		requests.put("http://%s/api/%s/lights/%s/state" % (self.ip, self.user, light), data=json.dumps(data))
	
	def fade(self, light, start_data, end_data):
		self.set_light(light, start_data)
		time.sleep(1)
		self.set_light(light, end_data)
		
	def is_on(self, light):
		#check whether light is in self.lights_dict
		if str(light) in self.lights_dict:
			response = requests.get("http://%s/api/%s/lights/%s" % (self.ip, self.user, light))
			return response.json()['state']['on']
			
	def sunset_fadeup(self):
		start_data = {}
		end_data = {}
		start_data['on'] = True
		start_data['bri'] = 0
		start_data['xy'] = self.sunset_colour
		
		end_data['on'] = True
		end_data['bri'] = 255
		end_data['transitiontime'] = 6000
		
		for i in range(1,self.number+1):
			if self.is_on(i) is False:
				self.fade(i, start_data, end_data)
			
	def sunrise_fadedown(self):
		start_data = {}
		end_data = {}
		start_data['on'] = True
		start_data['bri'] = 255
		start_data['xy'] = self.sunset_colour
		
		end_data['on'] = True
		end_data['bri'] = 0
		end_data['transitiontime'] = 6000
		
		for i in range(1,self.number+1):
			if self.is_on(i) is True:
				self.fade(i, start_data, end_data)
		time.sleep(605)
		for i in range(1,self.number+1):
			if self.is_on(i) is True:
				self.set_light(i, {"on": False})
