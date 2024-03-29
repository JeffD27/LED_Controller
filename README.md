# LED_Controller
## **A simple driver for the xbox controller to control LED light strips.**

This code is designed to be used with a Raspberry Pi 4 to control led strip lighting with any videogame controller (I used an X-Box Controller). 
Easily adjust the color with the joystick or set customized colors.

## The Circuit: 

![circuit](circuit.jpg)


The circuit that needs to built, will use a **2222a transistor** and a 10k resistor for every color that needs to be controlled. 

Each 10k resistor goes from gate of each transistor to ground. Note: it can also go between the gate of the mosfet and the source pin of the mosfet (as shown above) because the soure pin is also connected to ground). 

The GPIO pins connect to the gates of the transistors and also to one end of the 10k resistor.



12v ground should connect to the raspberry pi ground and to the source pin of each transistor (as well as the 10k resistor). 

12v positive should connect directly to positive on the strip lighting. 





This program is set up for 3 seperate light circuits that can each be controlled individually. Each circuit has red, blue, green channels each requiring a mosfet (a total of 9 mosfets are required in the 3 circuit configuration).
Although, not fully tested, the program should work fine with less than three circuits. 

##                                       Very Important: Please use the appropriate gpio pins  
                          

### Please use the following GPIO Pins for each circuit:
### Circuit One:

**Red:** GPIO 22

**Green:** GPIO 18

**Blue:** GPIO 23

### Circuit Two:

**Red:** GPIO 24

**Green:** GPIO 25

**Blue:** GPIO 21

### Circuit Three:

**Red:** GPIO 16

**Green:** GPIO 17

**Blue:** GPIO 27
                      
                            
                            
                            
Note: if different GPIO pins are used you will need to edit the python dictionary called self.pin_dict in [pwm_dma.py](/pwm_dma.py) with the appropriate pin numbers.



## Dependencies

This code uses the [Pigpio library](https://github.com/joan2937/pigpio). Please make sure the latest version is installed. No need to start the dameon as it is handled in code.
Please install the following modules as well:
schedule
asyncio


## How to use the controller:

#### Selecting a circuit to control:

To scroll through each circuit, hit the left joystick to the left or right. The lights that you selected will blink.

#### Unlock to make changes

Click down on the center of the left joystick to unlock and make changes. This prevents accidental light changes when the controller is handled. 

#### Adjust brightness

After unlocking, slowly bring the left joystick down or up to adjust the brightness. 

#### Adjust the color

Hit "X" for Blue, "A" for green, or "B" for red. Then use the left joystick to increase or decrease that color. 

#### Change the lights to a set color

Red: hit start then "B" 

Green: hit start then "A"

Blue: hit start then "X"

All White acrross all circuits: hit the middle Xbox logo. hit it again to return to your previous state.

#### Setting and selecting custom colors:

When adjusted to the color you like, click the joystick down in the center, then hold down "select" then hit any of the back buttons or "Y". The color is now set to that button. Change the color and hit that button to return to the customized color.

#### Reboot the Raspberry Pi

Hold down on the d-pad and hit the back right trigger button.

#### Change lights slowly with time

Hold down strat button then press select. Lights will blink green then change VERY slowly. To exit this mode, hit the back right upper paddle button. The lights will blink red to indicate the mode is off. 



