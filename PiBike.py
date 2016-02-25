#================================================import all the modules=============================================================#
import random
import time
from RPi import GPIO
from dot3k import backlight as b
from dot3k import lcd as l
from dot3k import menu
from dot3k import joystick
from math import pi
import mpylayer
#==========================================define all constants=====================================================================#
#define constants | e.g. Wheel length, GPIO pins, etc.

#Make all the calculations on the wheel
wheel_diameter = 20
wheel_circumference = wheel_diameter * pi #C = pi*d
wheel_unit = 'in'

#Just a catch to ensure wheels are the same unit
if wheel_unit == "in":
    wheel_circumference *= 2.54
    wheel_unit = "cm"    
if wheel_unit == "cm":
    #convert to meters
    wheel_circumference /= 100
    wheel_unit = "m"
wheel_circumference = round(wheel_circumference)
print wheel_circumference
total_dist_travelled = 0 #NOTE : unit is meters, it is represented as distance travelled (meters)

#============================================GPIO setup=============================================================================#
#setup GPIO pin numbers according to BCM
rev_count_power_pin = 16 #BOARD 36
rev_count_pin = 26 #BOARD 37
GPIO_TRIGGER = 5 #BOARD 29
GPIO_ECHO = 6 #BOARD 31

# Set pins as output and input for Ultrasonic Sensor & Reed Switch
GPIO.setmode(GPIO.BCM)
GPIO.setup(rev_count_power_pin, GPIO.OUT)#Reed Switch Power
GPIO.setup(rev_count_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)#Reed Switch On/Off check
GPIO.setup(GPIO_TRIGGER,GPIO.OUT)#US sensor
GPIO.setup(GPIO_ECHO,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)#US sensor

GPIO.output(rev_count_power_pin, GPIO.HIGH)#Turn on Power for reed switch
GPIO.output(GPIO_TRIGGER, False)
#============================================start HC-SR04==========================================================================#
time.sleep(0.5)
l.clear()
# Send 10us pulse to trigger
GPIO.output(GPIO_TRIGGER, True)
time.sleep(0.00001)
GPIO.output(GPIO_TRIGGER, False)
start = time.time()
#==========================================define MPLAYER functions=================================================================#
def load_one_song(songs_music_dir="//home//pi//music//"):
	mp = mpylayer.MPlayerControl()
	music_dir = songs_music_dir
	music_list = os.listdir(music_dir)
	mp.loadfile(music_dir[random.randint(0, (len(music_dir)-1)])
def load_mp():
    mp = mpylayer.MPlayerControl()
    music_dir = "//home//pi//music//"
    musix = os.listdir(music_dir)
    musicList = []
    #print music_dir
    print musix

    #Now lets generate all the filenames

    #first test for accurate values
    for i in musix:
        filename = music_dir + i
        print  music_dir + "\t" + i + "\t"+ filename 
        musicList.append(filename)

    print musicList
    #always escape code backslashes
    for i in musicList:
        mp.loadfile(i)
        print mp.filename
        print mp.length

def pause():
    mp.pause()
#======================================================INDICATOR FUNCTIONS==========================================================#
left_indicator = 20 #BOARD 38
right_indicator = 21 #BOARD 40
GPIO.setup(left_indicator, GPIO.OUT)
GPIO.setup(right_indicator, GPIO.OUT)
indic_state = "off" #states can be 'left'/'right'/'off'
#right indicator
@joystick.on(joystick.LEFT)
def right_indic(pin):
    global indic_state
    indic_state = "right"
    
#left indicator
@joystick.on(joystick.RIGHT)
def left_indic(pin):
    global indic_state
    indic_state = "left"
    
#indicator off
@joystick.on(joystick.BUTTON)
def off_indic(pin):
    global indic_state
    indic_state = "off"
    
#=========================================================MAIN LOOP=================================================================#
load_one_song()
x = True
while x == True:
    try:
        l.clear()

        #total distance travelled
        if GPIO.input(rev_count_pin) == GPIO.HIGH:
            total_dist_travelled += wheel_circumference
            time.sleep(0.002)
        time.sleep(0.1)
        l.set_cursor_position(0, 0)
        l.write('Distance: %f' %total_dist_travelled + ' ' + wheel_unit)
        
        # Send 10us pulse to trigger
        GPIO.output(GPIO_TRIGGER, True)
        time.sleep(0.00001)
        GPIO.output(GPIO_TRIGGER, False)
        start = time.time()
        while GPIO.input(GPIO_ECHO)==0:
            start = time.time()
        while GPIO.input(GPIO_ECHO)==1:
            stop = time.time()
        # Calculate pulse length
        elapsed = stop-start
        # Distance pulse travelled in that time is time
        # multiplied by the speed of sound (cm/s)
        distance = elapsed * 34300
        # That was the distance there and back so halve the value
        distance = distance / 2
        b.set_graph(distance / 100.0)
        #car alert system
        if distance < 40.0:
            l.write('Alert! Car!')
            b.rgb(255, 0, 0)
        elif distance > 40.0:
            b.rgb(0, 255, 0)

        #indicator on/off  direction
        if indic_state == "off":
            GPIO.output(left_indicator, False)
            GPIO.output(right_indicator, False)
            time.sleep(0.1)
        elif indic_state == "right":
            GPIO.output(right_indicator, True)
            GPIO.output(left_indicator, False)
            time.sleep(0.1)
            GPIO.output(right_indicator, False)
        elif indic_state == "left":
            GPIO.output(left_indicator, True)
            GPIO.output(right_indicator, False)
            time.sleep(0.1)
            GPIO.output(left_indicator, False)
        #distance travelled
        l.set_cursor_position(0, 1)
    except KeyboardInterrupt:
        x = False
#=======================================CLEANUP=====================================================================================#
l.clear()
b.off()
b.set_graph(0.0)
GPIO.cleanup()
