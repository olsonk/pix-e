import picamera
from time import sleep
from datetime import datetime
from os import system
import random, string
from twython import Twython
from gpiozero import Button, LED, PWMLED
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

########################
#
# Behaviour Variables
#
########################
num_frame = 8       # Number of frames in Gif
gif_delay = 15      # Frame delay [ms]
rebound = True      # Create a video that loops start <=> end
tweet = False       # Tweets the GIF after capturing


########################
#
# Twitter (Optional)
# Ensure 'tweet' behaviour-variable is True if you want to tweet pictures.
#
########################
APP_KEY = 'YOUR API KEY'
APP_SECRET = 'YOUR API SECRET'
OAUTH_TOKEN = 'YOUR ACCESS TOKEN'
OAUTH_TOKEN_SECRET = 'YOUR ACCESS TOKEN SECRET'

#setup the twitter api client
twitter = Twython(APP_KEY, APP_SECRET,
                  OAUTH_TOKEN, OAUTH_TOKEN_SECRET)


gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)

########################
#
# Define GPIO
#
########################

button = Button(19) #Button GPIO Pin
status_led = PWMLED(12) #Status LED GPIO Pin
pwr_led = LED(21) #ON/OFF LED Pin

########################
#
# Camera
#
########################
camera = picamera.PiCamera()
camera.resolution = (540, 405)
camera.rotation = 90
#camera.brightness = 70
camera.image_effect = 'none'

# Indicate ready status
status_led.blink()
pwr_led.blink()
print('System Ready')

def random_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

def tweet_pics():
    try:
        print('Posting to Twitter')
        photo = open(filename + ".gif", 'rb')
        response = twitter.upload_media(media=photo)
        twitter.update_status(status='Taken with #PIX-E Gif Camera', media_ids=[response['media_id']])
    except:
        # Display error with long status light
        status_led.pulse(2, 2)
        sleep(2)
        

try:
    while True:
        if button.is_pressed: # Button Pressed
        
            ### TAKING PICTURES ###
            print('Gif Started')
            status_led.on()

            randomstring = random_generator()
            for i in range(num_frame):
                camera.capture('{0:04d}.jpg'.format(i))

            ### PROCESSING GIF ###
            status_led.blink(0.5, 0.5)
            
            if rebound == True: # make copy of images in reverse order
                for i in range(num_frame - 1):
                    source = str(num_frame - i - 1) + ".jpg"
                    source = source.zfill(8) # pad with zeros
                    dest = str(num_frame + i) + ".jpg"
                    dest = dest.zfill(8) # pad with zeros
                    copyCommand = "cp " + source + " " + dest
                    system(copyCommand)
                    
            filename = '/home/pi/gifcam/gifs/' + randomstring + '-0'
            print('Processing')
            graphicsmagick = "gm convert -delay " + str(gif_delay) + " " + "*.jpg " + filename + ".gif" 
            system(graphicsmagick)
            system("rm ./*.jpg") # cleanup source images
            
            ts = datetime.now().isoformat()
            file = drive.CreateFile({'title': ts+".gif"})
            file.SetContentFile(filename+".gif")
            file.Upload()
            
            ### TWEETING ###
            if tweet == True:
                status_led.pulse(0.5, 0.5)
                tweet_pics()
            
            print('Done')
            print('System Ready')

        else : # Button NOT pressed
            ### READY TO MAKE GIF ###
            status_led.blink(2, 2)
            #sleep(0.05)
           
except:
    pass

