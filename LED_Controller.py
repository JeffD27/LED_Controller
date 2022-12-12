# /etc/init.d/Led_Controller.py
### BEGIN INIT INFO
# Provides:          sample.py
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Start daemon at boot time
# Description:       Enable service provided by daemon.
### END INIT INFO
import time
#time.sleep(2)
from inputs import devices
from inputs import get_gamepad
from datetime import datetime as dt
import datetime
from inputs import get_gamepad
import os

import sys

#check and make sure it's not already running
pid = str(os.getpid())
pidfile = "/tmp/led_controller.pid"
if os.path.isfile(pidfile):
	print("%s already exists, exiting" % pidfile)
	sys.exit()
file = open(pidfile, "w")
file.write(pid)
file.close

time.sleep(2)

import pigpio
from pwm_dma import PWM


while True:
	try:
		os.system("sudo pigpiod") #start the pigpio dameon.
		break
	except:
		print("Excepting")



#os.system("sudo pigpiod") #start pigpiod
class Led_Controller:

	def __init__(self):

		#set variables:
		self.pi = pigpio.pi()
		self.pwm = PWM()
		self.device_lst = []
		for device in self.pwm.devices_dict.keys():
			self.device_lst.append(device)
		self.selection = self.device_lst[0]
		self.x = 0
		self.start = dt.now()
		self.dv_lst_subsc = -1
		self.unlock = False
		self.color_select = None

		self.start_btn = False
		self.freeze_buttons = False
		self.customize = False
		self.color_dict = {} #for custom colors
		self.mode_color_dict = {}
		self.mode_button_pressed = False
		self.reserved_btns = ["ABS_X", "ABS_Y","ABS_RX", "ABS_RY", 'SYN_REPORT', "SYN_DROPPED", "BTN_THUMBL", "BTN_SELECT", "BTN_START", "BTN_NORTH", "BTN_SOUTH", "BTN_EAST"]


		for devices in self.pwm.devices_dict.keys(): #blink lights to show that it is on
			print('initating blink')
			self.blink_lights(device, (0, 200, 1000)) #arbitruary color. mostly blue with a little green
		while True:
			print("starting loop")

			self.events = get_gamepad()
			event_codes = []


			#reset time variables
			if self.unlock and dt.now() > self.unlock_time + datetime.timedelta(seconds = 10):
				self.unlock = False
			if self.start_btn and dt.now() > self.start_btn_time + datetime.timedelta(seconds = 3):
				self.start_btn = False
			if self.freeze_buttons and dt.now() > self.freeze_time + datetime.timedelta(seconds = 1):
				self.freeze_buttons = False


			for event in self.events: #iterate through any event triggered by the gamepad
				#print("type:", event.ev_type, "event code:", event.code, "state:", event.state)

				#reboot
				if event.code == "ABS_HAT0Y": #d-pad
					while event.state == 1: #while the d-pad is pressed
						for event_2 in get_gamepad(): #get the events going on at the same time
							if event_2.code == "ABS_RZ" and event_2.state > 100: #if the rear right trigger is pressed
								print("rebooting")
								os.system('sudo reboot') #reboot

				#scroll with left joystick to the right
				if event.code == "ABS_X" and event.state > 30000 and self.freeze_buttons == False: #state > 9000 means the joystick is over to the right far
					if self.unlock: self.unlock_time = dt.now()
					if self.x > 0 and ((dt.now() - self.start) > (datetime.timedelta(seconds = 1))):
						#self.x = 0
						print('resetting')
						self.start = dt.now()
						self.setup_blink_lights("forward")
						break

					if self.x > 0 and ((dt.now() - self.start) < (datetime.timedelta(seconds = .8))): # if the data comes within .8 seconds, ignore it
						#print("breaking")
						break
					self.setup_blink_lights("forward") #blink to let user know the selection

				#scroll with left joystick to the left
				elif event.code == "ABS_X" and event.state < -30000 and self.freeze_buttons == False: # < -9000 means the joystick is over to the left far
					#print(event.state, 'state')
					if self.unlock: self.unlock_time = dt.now()
					if self.x > 0 and ((dt.now() - self.start) > (datetime.timedelta(seconds = 1))):
						#self.x = 0
						self.start = dt.now()
						self.color_select = None
						self.setup_blink_lights("backward")
						break

					if self.x > 0 and ((dt.now() - self.start) < (datetime.timedelta(seconds = .8))): # if the data comes within .8 seconds, ignore it
						#print("breaking")
						break

				#unlock to change color
				elif event.code == "BTN_THUMBL": #push down on the center of the left joystick
					if self.unlock: self.unlock_time = dt.now()
					self.unlock = True
					self.color_select = None
					self.unlock_time = dt.now()

				#change color with left joystick
				elif event.code == "ABS_Y" and (event.state > 8000 or event.state < -8000):
					if self.unlock: self.unlock_time = dt.now()
					if self.unlock: self.freeze_buttons = True
					self.freeze_time = dt.now()
					#print(event.state, 'state')
					if self.unlock and self.color_select == None:
						self.adjust_brightness(event.state, "all three") #all three means all three colors
					elif self.unlock and self.color_select == 'red':
						self.adjust_brightness(event.state, "red")
					elif self.unlock and self.color_select == 'green':
						self.adjust_brightness(event.state, "green")
					elif self.unlock and self.color_select == 'blue':
						self.adjust_brightness(event.state, "blue")
				elif event.code == "BTN_EAST" and event.state == 1: #BTN_EAST is "B" on x-box, event state = 1 means it pressed

					if self.start_btn and self.selection is not None:
						print("making red")
						self.pwm.changeColor(self.selection, red = 1000, green = 0, blue = 0) #change the color to red

					else: self.color_select = 'red'

				#change color with start button
				elif event.code == "BTN_SOUTH" and event.state == 1: #this is "A" on the xbox controller
					if self.start_btn and self.selection is not None:
						print("making green")
						self.pwm.changeColor(self.selection, red = 0, green = 1000, blue = 0) #change the color to green

					else: self.color_select = 'green'
					self.start_btn = False

				elif event.code == "BTN_NORTH" and event.state == 1: #for some reason this is x on the xbox controller
					if self.start_btn and self.selection is not None:
						print("making blue")
						self.pwm.changeColor(self.selection, red = 0, green = 0, blue = 1000) #change the color to blue
						self.start_btn = False
					else: self.color_select = 'blue'


				elif event.code == "BTN_START" and event.state == 1:
					self.start_btn = True
					self.start_btn_time = dt.now()
				elif event.code == "BTN_MODE" and event.state == 1: #this is the xbox logo button
					if not self.mode_button_pressed: #if we are not already in white mode
						for device in self.pwm.devices_dict:
							self.mode_color_dict[device] = self.pwm.get_current_color(device) #keep track of current color to reuse after we change it back from white
							self.pwm.changeColor(device, red = 1000, green = 1000, blue = 1000) #turn all Circuits white
					else: #return to previos color
						for color_tup in self.mode_color_dict.values():
							red = color_tup[0]
							green = color_tup[1]
							blue = color_tup[2]
							device = {i for i in self.mode_color_dict if self.mode_color_dict[i]==color_tup}.pop()
							self.pwm.changeColor(device, red, green, blue) #change color back from white to previous color
					if self.mode_button_pressed == False: self.mode_button_pressed = True
					else: self.mode_button_pressed = False
				#customize
				elif event.code == "BTN_SELECT": #allow any button except reserved_btns to save a color
					self.unlock_customize(event.state)

				elif self.customize == True and event.code not in self.reserved_btns:
					if self.freeze_buttons == True: #things happen to fast on a controller, and sometimes you don't want buttons to do anything.
						continue
					if self.unlock: self.set_custom_color(event.code) #set color to button

				#if the button is a customized color button, change the color to that custom color
				elif event.code in self.color_dict.keys():
					red = self.color_dict[event.code][0]
					green = self.color_dict[event.code][1]
					blue = self.color_dict[event.code][2]
					self.pwm.changeColor(self.selection, red, green, blue)
			print('ending while loop')

	def unlock_customize(self, btn_select_state):
		if btn_select_state == 1:
			self.customize = True
		if btn_select_state == 0:
			self.customize = False




	def set_custom_color(self, btn):
		if btn in self.reserved_btns:
			return(None)
		color = self.pwm.get_current_color(self.selection)
		self.color_dict[btn] = color

		print(self.color_dict, "color_dict")



	def apply_movement_to_color(self, color, movement, scalor = 1): #color should be a tuple
		#print('applying movement of ', movement)
		movement = movement * -1 #up is up and down is down on the joystick
		#print(scalor, 'scalor!!!!!!!!!!!!!')
		color = color + (movement * scalor)
		if color > 1000: color = 1000
		if color < 0: color = 0
		return color

	def get_new_color_tup(self, current_color, movement):
		new_color_tup = ()
		if sum(list(current_color)) < 1:
			try:
				current_color = self.non_zero_color
			except AttributeError:
				print("AttributeError")
				current_color = (0, 0, 1)


		for color in current_color:
			other_colors = [x for x in current_color if x != color]
			color_sum = 0
			for color_a in other_colors:
				color_sum += color_a
			try:
				scalor = color/color_sum
			except ZeroDivisionError:
				print("zeroDivision")
				scalor = 1
			new_color = (self.apply_movement_to_color(color, movement, scalor))
			new_color_tup = new_color_tup + (new_color,)
		return new_color_tup

	def adjust_brightness(self, event_state, color_str):
		if self.selection == None:
			return None
		current_color = self.pwm.get_current_color(self.selection)
		if sum(list(current_color)) > 1:
			self.non_zero_color = current_color
		movement = event_state/4000
		if color_str == "all three":
			new_color_tup = self.get_new_color_tup(current_color, movement)

			print(new_color_tup, 'new color')
		elif color_str == 'red':
			new_color_tup = (self.apply_movement_to_color(current_color[0], movement), current_color[1], current_color[2])
		elif color_str == 'green':
			new_color_tup = (current_color[0],self.apply_movement_to_color(current_color[1], movement), current_color[2])
		elif color_str == 'blue':
			new_color_tup = (current_color[0], current_color[1], self.apply_movement_to_color(current_color[2], movement))



		red = new_color_tup[0]
		green = new_color_tup[1]
		blue = new_color_tup[2]

		print(red, green, blue)
		self.pwm.changeColor(self.selection, red, green, blue)

	def setup_blink_lights(self, direction):

		self.x += 1
		self.start = dt.now()
		self.start = dt.now()
		#print(self.dv_lst_subsc, 'subsc')
		#print(direction)
		if direction == "forward":
			self.dv_lst_subsc += 1
			#print('forward_+', self.dv_lst_subsc)

		if direction == "backward":
			self.dv_lst_subsc -= 1
			print('backward_-', self.dv_lst_subsc)
		if abs(self.dv_lst_subsc) == len(self.device_lst):
			self.dv_lst_subsc = 0
		self.selection = self.device_lst[self.dv_lst_subsc]
		#print(self.selection,'selection')
		current_color = PWM.get_current_color(self.pwm, self.selection)
		#print("blinking")
		current_color = self.pwm.get_current_color(self.selection)
		self.blink_lights(self.selection, current_color)

	def blink_lights(self, device, color):
		for i in range(5): #blink 5 times
			PWM.changeColor(self.pwm, device, 0, 0, 0) #turn lights off to make them blink
			time.sleep(.1)
			PWM.changeColor(self.pwm, device, color[0], color[1], color[2]) # turn lights on to make them blink
			time.sleep(.04)
			PWM.changeColor(self.pwm, self.selection, color[0], color[1], color[2]) #return lights to previous color
try:
	Led_Controller()
finally:
	os.unlink(pidfile) #for testing to see if program is already running
