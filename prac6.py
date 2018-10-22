#EEE3096S 2018
#Prac 6 / Mini Project A
#Twiddle Lock

#CTTKIE001
#DMNSTE001

#!/usr/bin/python3

###---IMPORTS---###
import RPi.GPIO as GPIO
import Adafruit_MCP3008
import time
import threading
import os
#import datetime
###-------------###

###---VARIABLES---###
# Service Button
buttonPin = 4

# Lock Line
lockLine = 17

# Unlock Line
unlockLine = 27

# Timout Pin
timoutPin = 2

# Mode Toggle Switch
secureToggle = 3

# SPI Lines
SPICLK = 11
SPIMISO = 9
SPIMOSI = 10
SPISS = 22

# Potentiometer
potCh = 0
prevADCValue = 0
deadband = 10 # 10 out of 1023

# States
terminating = False
directionState = 0 # -1=stop, 0=down, 1=up
lockState = 1 # 0=unlocked, 1 = locked
doneEnteringCode = 0 # has the user finished their code

# Passcode
word = [0, 0] # Duration, Direction
code = [[1, 0], [1, 1], [1, 0], [1, 1]] # hardcoded passcode
inputCode = [word]*16 # up to 16 words can be entered by the user
currentWordTime = 0 # time since the current word was started
currentWord = 0 # which word is being captured now

# Timing
sampleTime = 0.01
wordTimeout = 1 # time waited to signal the end of a word
codeTimout = 2 # time waited to signal the end of an input code

###-------------###

###---SETUP---###
# Pinmode
GPIO.setmode(GPIO.BCM)

# IO Pin Setup
GPIO.setup(buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(lockLine, GPIO.OUT)
GPIO.setup(unlockLine, GPIO.OUT)

# SPI Pins
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)

# ADC Object
mcp = Adafruit_MCP3008.MCP3008(clk=SPICLK, cs=SPISS, mosi=SPIMOSI, miso=SPIMISO)
###-------------###

###---BUTTON---###
# Interrupt Method
def buttonPush(channel):
	if (GPIO.input(channel) == GPIO.LOW): # Avoid trigger on button realease
		global inputCode, doneEnteringCode, directionState, prevADCValue
		# clear the input array
		inputCode = [word]*16
		# set ready for new input
		doneEnteringCode = 0
		directionState  = -1
		prevADCValue = getADCValue(potCh)
		# start timer
		timer()

# Interrupt Event Detection
GPIO.add_event_detect(resetPin, GPIO.FALLING, callback=buttonPush, bouncetime=100)
###-------------###

###---ADC---###
def getADCValue(chan):
	# Return value from ADC channel
	return mcp.read_adc(chan)
###-------------###

###---LOCK---###
def checkSecureCode():
	print("Checking Secure Code!")
	accessGranted = 0
	# check code

	if (accessGranted):
		if (lockState):
			unlock()
		else:
			lock()
	else:
		# invalid code
		lock()

def checkUnsecureCode():
	print("Checking Unsecure Code!")
	accessGranted = 0
	# check code
	
	if (accessGranted):
		if (lockState):
			unlock()
		else:
			lock()
	else:
		# invalid code
		lock()

def lock(): # issue a LOCK command
	global lockState
	# write lockLine HIGH for two seconds
	# play sound
	# update lockState variable
	lockState = 1
	print("Locked!")

def unlock(): # issue an UNLOCK command
	global lockState
	# write unlockLine HIGH for two seconds
	# play sound
	# update lockState variable
	lockState = 0
	print("Unlocked!")
###-------------###

###---TIMER---###
def timer():
	if (not terminating and not doneEnteringCode):	# Only continue if the parent thread is still running
													# and the code is still being entered
		# Start timer in new thread, delay and recall function
		threading.Timer(sampleTime, timer).start()

		global currentWordTime, prevADCValue, inputCode, directionState, currentWord, doneEnteringCode

		currentWordTime += sampleTime

		ADCValue = getADCValue(potCh)
		print(ADCValue)

		if ((ADCValue + deadband) > prevADCValue):
			# Going up
			prevADCValue = ADCValue
			if (directionState == 1):
				#continuing
				inputCode[currentWord] = [currentWordTime, directionState]
			else:
				#starting
				currentWordTime = 0
				directionState = 1
				currentWord += 1


		else if ((ADCValue - deadband) < prevADCValue):
			# Going down
			prevADCValue = ADCValue
			if (directionState == 0):
				#continuing
				inputCode[currentWord] = [currentWordTime, directionState]
			else:
				#starting
				currentWordTime = 0
				directionState = 0
				currentWord += 1

		else:
			# Stopped
			if ((currentWordTime - inputCode[currentWord][0]) >= wordTimeout):
				# end the current word
				directionState = -1

			if ((currentWordTime - inputCode[currentWord][0]) >= codeTimout):
				# end the capture session and flag for the code to be checked
				doneEnteringCode = 1

###-------------###

###---LOOP---###
try:
	os.system('clear')

	# Keep the program running, waiting for button presses
	while(1):
		if (doneEnteringCode):
			if (GPIO.input(secureToggle)):
				# secure mode selected
				checkSecureCode()
			else:
				# unsecure mode selected
				checkUnsecureCode()

except KeyboardInterrupt:
	print("losing")
	# Release all resources being used by this program
	terminating = True
	GPIO.cleanup()
###-------------###
