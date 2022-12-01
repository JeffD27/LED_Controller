import RPi.GPIO as GPIO
import time
from inputs import devices
from inputs import get_gamepad
from datetime import datetime as dt
import datetime
from inputs import get_gamepad
import pigpio
from pwm_dma import PWM

class Led_Controller:

	def __init__(self):
		#GPIO.setmode(GPIO.BCM)
		#GPIO.setwarnings(False)
		#GPIO.setup(24, GPIO.OUT)


		self.pi = pigpio.pi()
	#	self.pi.write(27, 1) test

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
		self.color_dict = {}
		self.mode_color_dict = {}
		self.mode_button_pressed = False
		self.reserved_btns = ["ABS_X", "ABS_Y","ABS_RX", "ABS_RY", 'SYN_REPORT', "SYN_DROPPED", "BTN_THUMBL", "BTN_SELECT", "BTN_START", "BTN_NORTH", "BTN_SOUTH", "BTN_EAST"]

		while True:

			self.events = get_gamepad()
			if self.unlock and dt.now() > self.unlock_time + datetime.timedelta(seconds = 10):
				self.unlock = False
			if self.start_btn and dt.now() > self.start_btn_time + datetime.timedelta(seconds = 3):
				self.start_btn = False
			if self.freeze_buttons and dt.now() > self.freeze_time + datetime.timedelta(seconds = 1):
				self.freeze_buttons = False


			for event in self.events: #iterate through any event triggered by the gamepad
				#print("type:", event.ev_type, "event code:", event.code, "state:", event.state)

				if event.code == "ABS_X" and event.state > 30000 and self.freeze_buttons == False: #state > 9000 means the joystick is over to the right far
					if self.unlock: self.unlock_time = dt.now()
					if self.x > 0 and ((dt.now() - self.start) > (datetime.timedelta(seconds = 1))):
						#self.x = 0
						print('resetting')
						self.start = dt.now()
						self.blink_lights("forward")
						break

					if self.x > 0 and ((dt.now() - self.start) < (datetime.timedelta(seconds = .8))): # if the data comes within .8 seconds, ignore it
						#print("breaking")
						break
					self.blink_lights("forward")

				elif event.code == "ABS_X" and event.state < -30000 and self.freeze_buttons == False: # < -9000 means the joystick is over to the left far
					print(event.state, 'state')
					if self.unlock: self.unlock_time = dt.now()
					if self.x > 0 and ((dt.now() - self.start) > (datetime.timedelta(seconds = 1))):
						#self.x = 0
						print('resetting')
						self.start = dt.now()
						self.color_select = None
						self.blink_lights("backward")
						break

					if self.x > 0 and ((dt.now() - self.start) < (datetime.timedelta(seconds = .8))): # if the data comes within .8 seconds, ignore it
						#print("breaking")
						break

				elif event.code == "BTN_THUMBL":
					if self.unlock: self.unlock_time = dt.now()
					self.unlock = True
					self.color_select = None
					self.unlock_time = dt.now()

				elif event.code == "ABS_Y" and (event.state > 8000 or event.state < -8000):
					if self.unlock: self.unlock_time = dt.now()
					if self.unlock: self.freeze_buttons = True
					self.freeze_time = dt.now()
					print(event.state, 'state')
					if self.unlock and self.color_select == None:
						self.adjust_brightness(event.state, "all three") #all three means all three colors
					elif self.unlock and self.color_select == 'red':
						self.adjust_brightness(event.state, "red")
					elif self.unlock and self.color_select == 'green':
						self.adjust_brightness(event.state, "green")
					elif self.unlock and self.color_select == 'blue':
						self.adjust_brightness(event.state, "blue")
				elif event.code == "BTN_EAST" and event.state == 1:
					if self.start_btn and self.selection is not None:
						print("making red")
						self.pwm.changeColor(self.selection, red = 1000, green = 0, blue = 0)
					else: self.color_select = 'red'

				elif event.code == "BTN_SOUTH" and event.state == 1:
					if self.start_btn and self.selection is not None:
						print("making green")
						self.pwm.changeColor(self.selection, red = 0, green = 1000, blue = 0)
					else: self.color_select = 'green'
				elif event.code == "BTN_NORTH" and event.state == 1: #for some reason this is x on the xbox controller

					if self.start_btn and self.selection is not None:
						print("making blue")
						self.pwm.changeColor(self.selection, red = 0, green = 0, blue = 1000)
					else: self.color_select = 'blue'
				elif event.code == "BTN_START" and event.state == 1:
					self.start_btn = True
					self.start_btn_time = dt.now()
				elif event.code == "BTN_MODE" and event.state == 1:
					if not self.mode_button_pressed:
						for device in self.pwm.devices_dict:
							self.mode_color_dict[device] = self.pwm.get_current_color(device)
							self.pwm.changeColor(device, red = 0, green = 0, blue = 1000)
					else:
						for color_tup in self.mode_color_dict.values():
							red = color_tup[0]
							green = color_tup[1]
							blue = color_tup[2]
							device = {i for i in self.mode_color_dict if self.mode_color_dict[i]==color_tup}.pop()
							self.pwm.changeColor(device, red, green, blue) #change color back from white to previous color
					if self.mode_button_pressed == False: self.mode_button_pressed = True
					else: self.mode_button_pressed = False
				elif event.code == "BTN_SELECT":
					self.unlock_customize(event.state)
				elif self.customize == True and event.code not in self.reserved_btns:
					if self.freeze_buttons == True:
						continue
					if self.unlock: self.set_custom_color(event.code)
				elif event.code in self.color_dict.keys():
					red = self.color_dict[event.code][0]
					green = self.color_dict[event.code][1]
					blue = self.color_dict[event.code][2]
					self.pwm.changeColor(self.selection, red, green, blue)


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
		print('applying movement of ', movement)
		movement = movement * -1 #up is up and down is down on the joystick
		print(scalor, 'scalor!!!!!!!!!!!!!')
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
				current_color = (0, 0, 1)


		for color in current_color:
			other_colors = [x for x in current_color if x != color]
			color_sum = 0
			for color_a in other_colors:
				color_sum += color_a
			try:
				scalor = color/color_sum
			except ZeroDivisionError:
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

	def blink_lights(self, direction):

		self.x += 1
		self.start = dt.now()
		self.start = dt.now()
		print(self.dv_lst_subsc, 'subsc')
		print(direction)
		if direction == "forward":
			self.dv_lst_subsc += 1
			print('forward_+', self.dv_lst_subsc)

		if direction == "backward":
			self.dv_lst_subsc -= 1
			print('backward_-', self.dv_lst_subsc)
		if abs(self.dv_lst_subsc) == len(self.device_lst):
			self.dv_lst_subsc = 0
		self.selection = self.device_lst[self.dv_lst_subsc]
		print(self.selection,'selection')
		current_color = PWM.get_current_color(self.pwm, self.selection)
		print("blinking")
		current_color = self.pwm.get_current_color(self.selection)
		for i in range(5): #blink 5 times
			PWM.changeColor(self.pwm, self.selection, 0, 0, 0) #turn lights off to make them blink
			time.sleep(.1)
			PWM.changeColor(self.pwm, self.selection, current_color[0], current_color[1], current_color[2]) # turn lights on to make them blink
			time.sleep(.04)

		PWM.changeColor(self.pwm, self.selection, current_color[0], current_color[1], current_color[2]) #return lights to previous color

Led_Controller()