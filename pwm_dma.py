#This pwm uses dma which is psuedo hardware i guess. more accurate than software pwm.
#gpio 12, 13, and 6 represent RGB respectively of background lights


import pigpio
import time

class PWM:
	def __init__(self):
		self.pi = pigpio.pi()
		print('running')
		self.devices_dict = {
			"bglights": ["bgR", "bgG", "bgB"], #Circuit one [Red, green blue]
			"shelves": ["shR", "shG", "shB"], #Circuit two [Red, green blue]
			"closet": ["clR", "clG", "clB"]} #Circuit three [Red, green blue]
		self.pin_dict = { #GPIO pin numbers. Make sure they correspond to the pins for your specific Circuits
			"bgR": 16, "bgG": 26, "bgB": 21, #Circuit one GPIO pin numbers
			"shR": 22, "shG": 18, "shB": 23, #Circuit two GPIO pin numbers
			"clR": 24, "clG": 25, "clB":27} #Circuit three GPIO pin numbers



		for key in self.pin_dict:
			pin = self.pin_dict[key]
			try:
				self.pi.set_PWM_range(pin, 1000) #change the range of the output voltage quantifier from the default of 0-250 to 0-1000
			except:
				return None
				


	def get_current_color(self, device): #device is the name of the Circuit. I used bglights, shelves, and closet in this code.
		pins = {"red" : self.pin_dict[self.devices_dict[device][0]],
				"green": self.pin_dict[self.devices_dict[device][1]],
				"blue": self.pin_dict[self.devices_dict[device][2]]}
		try:
			dutycycleRGB = (self.pi.get_PWM_dutycycle(pins["red"]),self.pi.get_PWM_dutycycle(pins["green"]),self.pi.get_PWM_dutycycle(pins["blue"])) #return a tuple of color values from 0-1000 in the form (r,g,b)

		except:
			print("DUTYCYCLERGB failed! Resetting color")
			dutycycleRGB = (pins["red"], 200, pins["green"], 800, pins["blue"], 1000) #set color to purple. Change the values to anything between 0-1000 to adjust default color.
		return dutycycleRGB
	def changeColor(self, device, red, green, blue): #rgb range 0 - 1000
		print(red, green, blue, 'Red, green, blue in pwm_dma')
		color_dict = {
			"bgR": red, "bgG": green, "bgB": blue,
			"shR": red, "shG": green, "shB": blue,
			"shR": red, "shG": green, "shB": blue,
			"clR": red, "clG": green, "clB": blue}

		device_list = self.devices_dict[device] #input device/Circuit as a key return list value of strings

		for color_line in device_list:
			#print("color_line", color_line)
			self.pi.set_PWM_dutycycle(self.pin_dict[color_line], color_dict[color_line]) #change the color
