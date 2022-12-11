#This pwm uses dma which is psuedo hardware i guess. more accurate than software pwm.
#gpio 12, 13, and 6 represent RGB respectively of background lights


import pigpio
class PWM:
	def __init__(self):
		self.pi = pigpio.pi()
		print('running')
		self.devices_dict = {
			"bglights": ["bgR", "bgG", "bgB"],
			"shelves": ["shR", "shG", "shB"],
			"closet": ["clR", "clG", "clB"]}
		self.pin_dict = {
			"bgR": 22, "bgG": 18, "bgB": 23,
			"shR": 24, "shG": 25, "shB": 21,
			"clR": 16, "clG": 17, "clB":27}



		for key in self.pin_dict:
			pin = self.pin_dict[key]
			self.pi.set_PWM_range(pin, 1000)
			#print(self.pi.get_PWM_range(pin), 'range')
			#print(self.pi.get_PWM_real_range(pin), 'real range')

	def get_current_color(self, device):
		#print([self.devices_dict[device][0]], 'xxxxxxxxxxxxxxxxxxxxxxx')
		pins = {"red" : self.pin_dict[self.devices_dict[device][0]],
				"green": self.pin_dict[self.devices_dict[device][1]],
				"blue": self.pin_dict[self.devices_dict[device][2]]}
		try:
			dutycycleRGB = (self.pi.get_PWM_dutycycle(pins["red"]),self.pi.get_PWM_dutycycle(pins["green"]),self.pi.get_PWM_dutycycle(pins["blue"])) #, self.pi.get_PWM_dutycycle(pins["green"]), self.pi.get_PWM_dutycycle(pins["blue"]))

		except:
			print("DUTYCYCLERGB")
			dutycycleRGB = (pins["red"], 200, pins["green"], 800, pins["blue"], 1000)
		return dutycycleRGB
	def changeColor(self, device, red, green, blue): #rgb range 0 - 1000
		print(red, green, blue, 'pwm-dma')

		color_dict = {
			"bgR": red, "bgG": green, "bgB": blue,
			"shR": red, "shG": green, "shB": blue,
			"shR": red, "shG": green, "shB": blue,
			"clR": red, "clG": green, "clB": blue}

		device_list = self.devices_dict[device] #input device as a key return list value of strings
		#print(device_list)
		for color_line in device_list:
			#print("color_line", color_line)
			self.pi.set_PWM_dutycycle(self.pin_dict[color_line], color_dict[color_line])


#changeColor("shelves",100, 500, 100)
'''
	#bglights
	pi.set_PWM_dutycycle(12, 0) #red
	pi.set_PWM_dutycycle(6, 130) #green
	pi.set_PWM_dutycycle(13, 800) #blue
	#shelves
	pi.set_PWM_dutycycle(4, 0) #red
	pi.set_PWM_dutycycle(27, 30)#green
	pi.set_PWM_dutycycle(22, 255)#blue
	#closet
	pi.set_PWM_dutycycle(23, 30) #red
	pi.set_PWM_dutycycle(24, 30)#green
	pi.set_PWM_dutycycle(25, 10)#blue
'''
