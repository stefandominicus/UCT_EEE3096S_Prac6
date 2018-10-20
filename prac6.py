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
timeoutPin = 2

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
deadband = 20 # 10 out of 1023

# States
terminating = 0
directionState = 0 # -1=stop, 0=down, 1=up
lockState = 1 # 0=unlocked, 1 = locked
doneEnteringCode = 0 # has the user finished their code

# Passcode
word = [0, 0] # Duration, Direction
MAX_NUMBER_OF_WORDS = 16
code = [[1, 0], [2, 1], [1, 0], [1, 1], [3, 0]] # hardcoded passcode
inputCode = [word] * MAX_NUMBER_OF_WORDS # up to n words can be entered by the user
currentWordTime = 0 # time since the current word was started
currentWord = -1 # which word is being captured now

# Timing
sampleTime = 0.1
wordTimeout = 0.5 # time waited to signal the end of a word
codeTimout = 2 # time waited to signal the end of an input code
timing = 0
stopped = 0 #debug
durationTolerance = 0.5
###-------------###

###---SETUP---###
# Pinmode
GPIO.setmode(GPIO.BCM)

# IO Pin Setup
GPIO.setup(buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(lockLine, GPIO.OUT)
GPIO.setup(unlockLine, GPIO.OUT)
GPIO.setup(timeoutPin, GPIO.OUT)
GPIO.setup(secureToggle, GPIO.IN, pull_up_down=GPIO.PUD_UP)


# SPI Pins
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPISS, GPIO.OUT)

# ADC Object
mcp = Adafruit_MCP3008.MCP3008(clk=SPICLK, cs=SPISS, mosi=SPIMOSI, miso=SPIMISO)
###-------------###

###---BUTTON---###
# Interrupt Method
def buttonPush(channel):
	if (GPIO.input(channel) == GPIO.LOW): # Avoid trigger on button realease
		global inputCode, doneEnteringCode, directionState, prevADCValue, timing, currentWord, currentWordTime, stopped
		os.system('clear')
		# clear the input array
		inputCode = [word]*MAX_NUMBER_OF_WORDS
		# set ready for new input
		doneEnteringCode = 0
		timing = 1
		stopped = 0 #debug
		directionState  = -1
		prevADCValue = getADCValue(potCh)
		currentWordTime = 0 # time since the current word was started
		currentWord = -1
		timer()

# Interrupt Event Detection
GPIO.add_event_detect(buttonPin, GPIO.FALLING, callback=buttonPush, bouncetime=200)
###-------------###

###---ADC---###
def getADCValue(chan):
	# Return value from ADC channel
	return mcp.read_adc(chan)
###-------------###

###---LOCK---###
def checkSecureCode():
	print("Checking Secure Code!")
	accessGranted = 1
	# check code
	if (currentWord == len(code) - 1):
		#inputCode has the right number of words
		for i in range(currentWord):
			if (inputCode[i][1] != code[i][1] or abs(inputCode[i][0] - code[i][0]) > durationTolerance):
				#word is incorrect
				accessGranted = 0
				break
	else:
		#wrong number of words
		accessGranted = 0

	if (accessGranted):
		os.system('omxplayer success.mp3 > /dev/null 2 >&1')
		if (lockState):
			unlock()
		else:
			lock()
	else:
		# invalid code
		print("Invalid Code")
		#Play Sound
		os.system('omxplayer fail.mp3 > /dev/null 2 >&1')

def checkUnsecureCode():
	print("Checking Unsecure Code!")
	accessGranted = 1
	# check code
	if (currentWord == len(code) - 1):
		#input code has the right number of words
		sortedCode = sorted(code, key=lambda l:l[0], reverse=True)
		sortedInputCode = sorted(inputCode, key=lambda l:l[0], reverse=True)
		for i in range(currentWord):
			if (abs(sortedInputCode[i][0] - sortedCode[i][0]) > durationTolerance):
				#duration is incorrect
				accessGranted = 0
				break
	else:
		#wrong number of words
		accessGranted = 0

	if (accessGranted):
		os.system('omxplayer success.mp3 > /dev/null 2 >&1')
		if (lockState):
			unlock()
		else:
			lock()
	else:
		# invalid code
		print("Invalid Code")
		#Play sound
		os.system('omxplayer fail.mp3 > /dev/null 2 >&1')

def lock(): # issue a LOCK command
	print("Locking...")
	# write lockLine HIGH for two seconds
	GPIO.output(lockLine, GPIO.HIGH)
	time.sleep(2)
	GPIO.output(lockLine, GPIO.LOW)
	# update lockState variable
	global lockState
	lockState = 1
	print("Locked!")

def unlock(): # issue an UNLOCK command
	global lockState
	# write unlockLine HIGH for two seconds
	GPIO.output(unlockLine, GPIO.HIGH)
	time.sleep(2)
	GPIO.output(unlockLine, GPIO.LOW)
	# update lockState variable
	lockState = 0
	print("Unlocked!")
###-------------###

###---TIMER---###
def timer():
	if (not terminating and not doneEnteringCode and timing):	# Only continue if the parent thread is still running
									# and the code is still being entered
		# Start timer in new thread, delay and recall function
		threading.Timer(sampleTime, timer).start()

		global currentWordTime, prevADCValue, inputCode, directionState, currentWord, doneEnteringCode, stopped

		currentWordTime += sampleTime

		ADCValue = getADCValue(potCh)
		#print(ADCValue)

		if (ADCValue  > (prevADCValue + deadband)):
			# Going up
			stopped = 0
			prevADCValue = ADCValue
			if (directionState == 1):
				#continuing
				inputCode[currentWord] = [round(currentWordTime, 1), directionState]
			else:
				#starting
				print(inputCode[currentWord])
				currentWordTime = 0
				directionState = 1
				GPIO.output(timeoutPin, GPIO.LOW)
				if (currentWord == MAX_NUMBER_OF_WORDS - 1):
					doneEnteringCode = 1
				else:
					currentWord += 1

		elif (ADCValue < (prevADCValue - deadband)):
			# Going down
			stopped = 0
			prevADCValue = ADCValue
			if (directionState == 0):
				#continuing
				inputCode[currentWord] = [round(currentWordTime, 1), directionState]
			else:
				#starting
				print(inputCode[currentWord])
				currentWordTime = 0
				directionState = 0
				GPIO.output(timeoutPin, GPIO.LOW)
				if (currentWord == MAX_NUMBER_OF_WORDS - 1):
					doneEnteringCode = 1
				else:
					currentWord += 1

		else:
			# Stopped
			if (currentWord != -1 and (currentWordTime - inputCode[currentWord][0]) >= wordTimeout and not stopped):
				# end the current word
				global stopped
				stopped = 1
				#print(inputCode)
				print("Ready for new word")
				directionState = -1
				GPIO.output(timeoutPin, GPIO.HIGH)

			if ((currentWordTime - inputCode[currentWord][0]) >= codeTimout):
				# end the capture session and flag for the code to be checked
				print ("codeTimeout")
				print(inputCode)
				doneEnteringCode = 1
				GPIO.output(timeoutPin, GPIO.LOW)

###-------------###

###---LOOP---###
try:
	os.system('clear')
	lock() #make sure the system starts off being locked
	# Keep the program running, waiting for button presses
	while(1):
		if (doneEnteringCode and timing):
			global timing
			timing = 0
			if (GPIO.input(secureToggle)):
				# secure mode selected
				checkSecureCode()
			else:
				# unsecure mode selected
				checkUnsecureCode()

except KeyboardInterrupt:
	print("losing")
	# Release all resources being used by this program
	terminating = 1
	GPIO.cleanup()
###-------------###
