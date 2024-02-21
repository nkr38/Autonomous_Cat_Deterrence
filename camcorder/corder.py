
#!/usr/bin/python
import time, datetime

#time.sleep(30)

import RPi.GPIO as GPIO
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder, Quality
from picamera2.outputs import FfmpegOutput

from pathlib import Path

FRAMERATE = 30
size = (2304,1296)
BITRATE = 10000000
LED_PIN = 17
BUT_PIN = 15
DEBOUNCE_TIME = 0.001

recording = False
encoder = H264Encoder(40000000)
last_time_called = datetime.datetime.now()

def startup_blink():
	GPIO.output(LED_PIN,GPIO.HIGH)
	time.sleep(0.2)
	GPIO.output(LED_PIN,GPIO.LOW)
	time.sleep(0.2)
	GPIO.output(LED_PIN,GPIO.HIGH)
	time.sleep(0.2)
	GPIO.output(LED_PIN,GPIO.LOW)
	time.sleep(0.2)
	GPIO.output(LED_PIN,GPIO.HIGH)
	time.sleep(0.2)
	GPIO.output(LED_PIN,GPIO.LOW)
	time.sleep(0.2)
	

def button_callback(channel):
	global recording, encoder
	time_called = datetime.datetime.now()
	td = (time_called - globals()["last_time_called"]).total_seconds()
	globals()["last_time_called"] = time_called
	# print(f"{td}s since last callback")

	#if td > 1:
	r = globals()["recording"]
	# print(f"recording = {r}")
	if not globals()["recording"]: # start recording
		globals()["recording"] = True
		GPIO.output(LED_PIN, GPIO.HIGH)
		now = datetime.datetime.now().strftime("%H-%M-%S_%d-%m-%Y")
		if Path("/media/raspi/catdrive/").is_dir():
			output = FfmpegOutput(f'/media/raspi/catdrive/vid_{now}.mp4')
		else :
			output = FfmpegOutput(f'vid_{now}.mp4')
		picam2.start_recording(encoder, output)
		print("recording!")
	else: # stop recording
		globals()["recording"] = False 
		GPIO.output(LED_PIN, GPIO.LOW)
		picam2.stop_recording()
		print("recording done!")



picam2 = Picamera2()
video_config = picam2.create_video_configuration({"size":size})
picam2.video_configuration.controls.FrameRate = FRAMERATE
print(picam2.video_configuration.controls.FrameRate)
picam2.configure(video_config)



GPIO.setmode(GPIO.BCM)
GPIO.setup(BUT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.output(LED_PIN, GPIO.LOW)
startup_blink()
GPIO.add_event_detect(BUT_PIN,GPIO.FALLING,callback=button_callback)


while True:
	pass
	# if GPIO.input(BUT_PIN) == GPIO.HIGH:	
	# 	GPIO.output(LED_PIN, GPIO.HIGH)
	# 	#time.sleep(1)
	# else:
	# 	GPIO.output(LED_PIN, GPIO.LOW)
GPIO.cleanup()
