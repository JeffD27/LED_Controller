# LED_Controller
## **A simple driver for the xbox controller to control LED light strips.**

This code is designed to be used with a Raspberry Pi 4 to control led strip lighting with any videogame controller (I used an X-Box Controller). 


## The Circuit: 

![circuit](https://user-images.githubusercontent.com/53206149/206923802-ec7b8638-f509-4cdd-aa1a-2599685ec2c4.png)

The circuit that needs to built, will use a mosfet and a 10k resistor for every color that needs to be controlled. 

The 10k resistor goes from gate of the mosfet to ground (or to the source pin on the mosfet, which is also connected to ground). 

The GPIO pins connect to the gate of the mosfet and also one end of the 10k resistor.

12v ground should connect to the raspberry pi ground and to the source pin of each mosfet (as well as the 10k resistor). 

12v positive should connect directly to positive on the strip lighting. 

Each negative color wire from the strip lights should connect to a drain on a mosfet. 

This program is set up for 3 seperate light circuits that can each be controlled individually. Each circuit has red, blue, green channels each requiring a mosfet (a total of 9 mosfets are required in the 3 circuit configuration).
Although, not fully tested, the program should work fine with less than three circuits. 

##                                       Very Important: Please use the appropriate gpio pins  
                          

### Please use the following GPIO Pins for each circuit:
### Circuit One:

**Red:** GPIO 22

**Green:** GPIO 18

**Blue:** GPIO 23

Circuit Two:

**Red:** GPIO 24

**Green:** GPIO 25

**Blue:** GPIO 21

Circuit Three:

**Red:** GPIO 16

**Green:** GPIO 17

**Blue:** GPIO 27
                      
                            
                            
                            
Note: if a different GPIO pins are used you will need to edit the python dictionary called self.pin_dict in [pwm_dma.py](/pwm_dma.py).


## Dependencies

This code uses the [Pigpio library](https://github.com/joan2937/pigpio). Please make sure the latest version is installed. No need to start the dameon as it is handled in code.

## How to use the controller:

#### Selecting a circuit to control:

To scroll through each circuit, hit the left joystick to the left or right. The lights that you selected will blink.

#### Unlock to make changes

Hit down on the left joystick to unlock and make changes. This prevents accidental light changes when the controller is handled. 

#### Adjust brightness

After unlocking, slowly bring the left joystick down or up to adjust the brightness. 

#### Adjust the color

Hit "X" for Blue, "A" for green, or "B" for red. Then use the left joystick to increase or decrease that color. 

#### Change the lights to a set color

Red: hit start then "B" 

Green: hit start then "A"

Blue: hit start then "X"

All White acrross all circuits: hit the middle Xbox logo. hit it again to return to your previous state.

####Setting and selecting custom colors:

When adjusted to the color you like hold down "select" then hit any of the back buttons or "Y". The color is now set to that button. Change the color and hit that button to return to the customized color.





