# /etc/init.d/Led_Controller.py
### BEGIN INIT INFO
# Provides:          sample.py
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Start daemon at boot time
# Description:       Enable service provided by daemon.


#### to do next. create a file to keep track if this program is running. exit if running.
### END INIT INFO
import time
#if run from boot argv should be 0 else 1:
import inputs
from inputs import devices
from inputs import get_gamepad
from datetime import datetime as dt
import datetime
import random
import sys
import os
import re
import csv
import logging
import pigpio
from pwm_dma import PWM
import schedule 
import time
import asyncio
import server_for_goog
logging.basicConfig(filename='log1.log', encoding='utf-8', level=logging.DEBUG)




class Led_Controller:
	
	def __init__(self, argv):
		#return 0
		logging.info('running' + str(dt.now()))
		#if len(argv) == 1:
	#		if argv.pop() == "0": #this means it is running from boot
		#		print("sleeping...") 
		#		logging.info('sleeping')
		#		time.sleep(10) #give it time for the pi to connect to a network etc.
		self.pig_count = 0
		self.connect_pigpio()
		self.pwm = PWM()
		self.setVariables()
		
		asyncio.run(self.main())
		
		

	def setVariables(self):
		
		
		
		self.device_lst = []
		for device in self.pwm.devices_dict.keys(): 
			self.device_lst.append(device)
		self.selection = self.device_lst[0]
		self.x = 0
		self.start = dt.now()
		self.dv_lst_subsc = -1
		self.unlock = False
		self.color_select = None
		self.color_changing = False
		self.start_btn = False
		self.freeze_buttons = False
		self.customize = False
		self.color_dict = {} #for custom colors
		self.mode_color_dict = {}
		self.off_color_dict = {}
		self.mode_button_pressed = False
		self.btn_west = False
		self.bumpers_pressed = False
		self.off_locked = True
		
		
		self.add_dict = {'red': 1, 'green' : 1, 'blue' : 1} # 1 means add     0 means subtract
		

		
		self.reserved_btns = ["ABS_X", "ABS_Y","ABS_RX", "ABS_RY", 'SYN_REPORT', "SYN_DROPPED", "BTN_THUMBL", "BTN_SELECT", "BTN_START", "BTN_WEST", "BTN_NORTH", "BTN_SOUTH", "BTN_EAST"]
		
	
		
		
		

	async def main(self):			#print("starting loop")
	
			
		self.initiate_blink()
		self.return_to_previous()
		
		print('starting loop')
		
		
		
		#await self.run_schedule()
		
		#print('scheduled')
		while True: 
			asyncio.gather(self.get_controller_event(), self.save())
			await asyncio.sleep(1)

	async def iterate_gamepad(self, events):
		for event in events: #iterate through any event triggered by the gamepad
			#print( "event code:", event.code, "state:", event.state)
		
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
			
			elif event.code == "BTN_TR" and event.state == 1: #buton west is the back right top paddle button
				print('west!!!!!!!!!!!!!!!!!')
				if self.color_changing: #if color changing is on, shut it off (shut off color changing)
					print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
					for device in self.device_lst:
						self.blink_lights(device, (1000, 0, 0))
						self.return_to_previous()
						schedule.cancel_job(self.sched_event)
						print('CANCELED!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
					self.color_changing = False
					break
				elif not self.btn_west: #if we are not already in OFF mode
					self.current_color = self.pwm.get_current_color(self.selection) #keep track of current color to reuse after we change it back from white
					self.pwm.changeColor(self.selection, red = 0, green = 0, blue = 0) #turn all Circuits off
				else: #return to previos color
					red, green, blue = self.current_color[0], self.current_color[1], self.current_color[2]
					#print(red, green, blue, "RED GREEN BLUEEEEEE")
					self.pwm.changeColor(self.selection, red, green, blue) #change color back from off to previous color
				if self.btn_west == False: self.btn_west = True
				else: self.btn_west = False

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
				print('start')
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
			
		
			
				
			#turn off all leds
			elif event.code == "BTN_TL" and event.state == 1:
				self.off_locked = False
			elif event.code == "BTN_TR" and event.state == 1:
				if self.off_locked:
					break
				if not self.bumpers_pressed: #if we are not already in OFF mode
					for device in self.pwm.devices_dict:
						self.off_color_dict[device] = self.pwm.get_current_color(device) #keep track of current color to reuse after we change it back from white
						self.pwm.changeColor(device, red = 0, green = 0, blue = 0) #turn all Circuits off
				else: #return to previos color
					for color_tup in self.off_color_dict.values():
						red = color_tup[0]
						green = color_tup[1]
						blue = color_tup[2]
						device = {i for i in self.off_color_dict if self.off_color_dict[i]==color_tup}.pop()
						self.pwm.changeColor(device, red, green, blue) #change color back from off to previous color
				if self.bumpers_pressed == False: self.bumpers_pressed = True
				else: self.bumpers_pressed = False
			#customize
			elif event.code == "BTN_SELECT": 
				if self.start_btn == True: #if start button is was pressed and held first then:
					print('starting color change$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$4')
					for device in self.device_lst:
						self.blink_lights(device, (0,1000,0))
						self.return_to_previous()
					self.color_changing = True
					self.sched_event = schedule.every(.5).seconds.do(self.change_color_w_time) #start time change mode
					self.sched_event.run()
					#asyncio.gather(self.run_schedule(), self.get_controller_event())
					
				else:		
					print('unlocked')
					self.unlock_customize(event.state)#allow any button except reserved_btns to save a color

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
			
		#print('ending while loop')
		
		



		print('found events')
		#
		if self.unlock and dt.now() > self.unlock_time + datetime.timedelta(seconds = 10):
			self.unlock = False
		if self.start_btn and dt.now() > self.start_btn_time + datetime.timedelta(seconds = 1):
			self.start_btn = False
		if self.freeze_buttons and dt.now() > self.freeze_time + datetime.timedelta(seconds = .5):
			self.freeze_buttons = False

			#loop.stop()

	async def save(self):
		print("SAVE IS RUNNING!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!########################################")
		for device in self.pwm.devices_dict.keys():
			color = self.pwm.get_current_color(device)
			#print(color)
			if len(color) > 3:
				#print('shrinking')
				color = (color[1], color[3], color[5]) #fixes a glitch from pwm
			#print(color, 'cooollllerr!')
			self.write_to_previous_state(device, color)
			self.cleanup_previous_state()
	async def run_schedule(self):
		#await asyncio.sleep(1)
		print('color changing running sched!!!!')
		await schedule.run_pending()
			
				
		

	async def get_controller_event(self):
		while True:
			print("seeking controller event")
			#await asyncio.sleep(1)
			events = []
			while True:
				
				try:
					events.append(inputs.get_gamepad()[0])
					break
				except inputs.UnpluggedError:
					print("gamepad is not connected")
					asyncio.sleep(5)
					continue
				except Exception as e:
					print(e)
					break
			#print('got gamepad')4
			await self.iterate_gamepad(events)
			await asyncio.sleep(.01)
	def unlock_customize(self, btn_select_state):
		if btn_select_state == 1:
			self.customize = True
		if btn_select_state == 0:
			self.customize = False
	
	def read_previous_state(self):
		colors = []
		print('reading_file')
		with open('previous_state.csv', mode='r') as csv_file:	
			#print('reading...')
			csv_reader = csv.reader(csv_file)
			print(csv_reader)
			i = 0
			for line in csv_reader:
				i+=1
				print(line, 'line')
				for txt in line:
					if re.search('\(', txt):
						search = re.search('^\((\d+),\s*(\d+),\s*(\d+)', txt)
						#print(search, 'here')
						red = search.group(1)
						green = search.group(2)
						blue = search.group(3)
						#print(red, green, blue)
					elif re.search('[a-z]{3,}', txt):
						device = re.search('[a-z]{3,}', txt).group()
						
				colors.append([device, red, green, blue])
		return(colors)	
				
	def write_to_previous_state(self, device, rgb_tup):
		with open('previous_state.csv', mode = 'a+') as csv_file:
			writer = csv.writer(csv_file, delimiter=',')
		
			writer.writerow({device, rgb_tup})
			#print('written', rgb_tup)

	def cleanup_previous_state(self):
		with open('previous_state.csv', mode = 'r') as f:
			lines = f.readlines()
		with open('previous_state.csv', mode = 'w') as f:
			for number, line in enumerate(lines):
				if number > (len(lines) - 4):
					f.write(line)
					
	def calculate_color_change(self, color, add, rand): #color is an int (not tupple) add is bolean (subtract = False)
		if add:
			new_color = color + rand 
			print("new color equals %s" % new_color)
		else:
			new_color = color - rand
		return new_color
	def change_color_w_time(self):
		print('color changing')
		for device in self.device_lst:
			print('color changing')
			print(device, 'device')

			current_color = self.pwm.get_current_color(device)
			print(current_color, 'current_color!')
			i = 0
			dict_convert_i = {0 : 'red', 1 : 'green', 2 : 'blue'}
			new_color_tup= ()
			for color in current_color:
				rand = random.randrange(1,100)
				#print(self.add_dict[dict_convert_i[i]], "$$$$$$$$$444444444444444444444444444444444444444444444444444")
				new_color = self.calculate_color_change(current_color[i], self.add_dict[dict_convert_i[i]], rand)
				print(new_color, "new color")
				if new_color > 1000:
					self.add_dict[dict_convert_i[i]] = 0
					#print( self.add_dict[dict_convert_i[i]], 'ppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppp')
					new_color = self.calculate_color_change(current_color[i], self.add_dict[dict_convert_i[i]], rand)
					
				elif new_color < 0 :
					self.add_dict[dict_convert_i[i]] = 1
					new_color = new_color*-1 #all this complex bs does is decide whether or add or sub color
				new_color_tup += (new_color, )
				print('new color tup', new_color_tup)
				i += 1
			
			self.pwm.changeColor(device, new_color_tup[0], new_color_tup[1], new_color_tup[2]) #change color
			
			
			
			

			

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

	def adjust_brightness(self, event_state, color_str): #color str = "red", "green", "blue" or "all three"
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
			PWM.changeColor(self.pwm, device, color[0], color[1], color[2]) #return lights to previous color
	def connect_pigpio(self):
		print("connecting")
		#self.pi = pigpio.pi('soft', 8888)
		#logging.info('connecting')
		self.pig_count += 1
		print(os.system('sudo pigs t'), 'here')
		os.system('sudo killall pigpiod')
		time.sleep(7)
		print(os.system('sudo pigs t'), 'here2: pigpiod killed')
	#	if not os.system('sudo pigs t') > 1:
		print('starting pigpiod', os.system('sudo pigs t'))
		os.system("sudo pigpiod") #start the pigpio dameon.
		
		time.sleep(5)
	
	def return_to_previous(self):
		
		print('return to previous')
		try:
			prev_state = self.read_previous_state()
			print(prev_state)
			for device_color_tup in prev_state:
				#print(device_color_tup, 'tup')
				device = device_color_tup[0]
				#print(device, 'device @#@')
				red, green, blue = device_color_tup[1], device_color_tup[2], device_color_tup[3]
				#print(red, green, blue, 'red green blue $$$$$$$$$$$$$$$$$$$$$$$$$$$@@@@@@@@@@@@@@@@@@@@')
				
				self.pwm.changeColor(device, red, green, blue)
		except Exception as e:
			print(e)
			
	def initiate_blink(self):
		try:
			for device in self.pwm.devices_dict.keys():
				#print(device, 'device @#@')
				red, green, blue = (0, 200, 1000)
				#print(red, green, blue, 'red green blue $$$$$$$$$$$$$$$$$$$$$$$$$$$@@@@@@@@@@@@@@@@@@@@')
				
				self.blink_lights(device, (red, green, blue))
			
			
		except Exception as e:
			print(e)
			logging.info('excepting')
			if self.pig_count > 20:
				raise		
			else:
				print('cant connect sleeping')
				time.sleep(20)
				self.connect_pigpio()
				#os.system("sudo pigpiod")
			
				
				
if __name__=="__main__": 	Led_Controller(sys.argv[1:])
	#exc_type, exc_obj, exc_tb = sys.exc_info()
	#logging.debug(e, dt.now())
#finally:
	#os.unlink(pidfile) #for testing to see if program is already running
