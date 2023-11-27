import RPi.GPIO as GPIO
from time import sleep

#this should be hardware pwm. Hardware only has 2 "channels" (but 4 pins somehow?) and can only run 2 different things. I need at least 9. 

ledpin = 12				# PWM pin connected to LED
GPIO.setwarnings(False)			#disable warnings
GPIO.setmode(GPIO.BOARD)		#set pin numbering system
GPIO.setup(ledpin,GPIO.OUT)
pi_pwm = GPIO.PWM(ledpin,1000)		#create PWM instance with frequency
pi_pwm.start(0)				#start PWM of required Duty Cycle 


	

while True:
	pi_pwm.ChangeDutyCycle(100)
	sleep(20)
	pi_pwm.ChangeDutyCycle(30)
	sleep(20)
	pi_pwm.ChangeDutyCycle(50)
'''	
    for duty in range(0,101,1):
        pi_pwm.ChangeDutyCycle(duty) #provide duty cycle in the range 0-100
        #sleep(0.01)
    #sleep(0.5)
    
    for duty in range(100,-1,-1):
        pi_pwm.ChangeDutyCycle(duty)
        #sleep(0.01) 
    #sleep(0.5)
'''	
