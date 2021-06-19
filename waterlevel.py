from Adafruit_IO import MQTTClient
from flask import Flask, render_template, request
import datetime
import time
import json
import RPi.GPIO as GPIO


IO_URL= "io.adafruit.com"
IO_SERVERPORT=1883
IO_USERNAME ="shastaneb09"
IO_KEY ="aio_crJF04lxjWPF2dCHUXS78st0KbL0"
prevLampStatus=False

client = MQTTClient(IO_USERNAME, IO_KEY, service_host=IO_URL)
app = Flask(__name__)


@app.route("/")
def index():

    templateData = {
            'levels'  :    []
        }
    return render_template('water-ui.html', **templateData)

@app.route('/water/level', methods=['GET'])
def measureWaterLevel():

   #collect the sensor data and send it as response
   #Run infintely until user interrupts
        # Define Static variables, file names and time format
        #pollTime below is set to 1 second
        #Besides the below pins, I use pin 1 for 3.3V
        client.connect()
        print('connected from Adafruit IO!')

        gPin = 7; yPin = 11; oPin = 23

        pollTime = 1; prevStatus = -1; timeFormat = "%I:%M:%S %p"

        #Setup GPIO
        GPIO.setwarnings(False); GPIO.setmode(GPIO.BOARD)
        #Setup various pins

        GPIO.setup([oPin,yPin,gPin], GPIO.IN, GPIO.PUD_DOWN)

        orange = GPIO.input(oPin); yellow = GPIO.input(yPin); green = GPIO.input(gPin)
        status = (green * 4) + (yellow * 2) + (orange * 1)
          


            #If status changes, set level indicator as red, orange, yellow or green  in that order
            # red (no pin) is on when all red, yellow and green are off.
        if status != prevStatus:
            print("previous ",prevStatus)
            print("current ", status)
            levelIndicator = ((("red","orange")[orange == 1],"yellow")[yellow == 1],"green")[green == 1]
            prevStatus = status
            currentTime = datetime.datetime.now().strftime(timeFormat)
            #print ("Status of water level at %s is %s \r\n" % (currentTime, levelIndicator))

            levelIndicator='green'
            colours = ["green", "yellow", "orange", "red"]

            levels =[]

            if levelIndicator =='green':
                levels=colours[0:4]
            elif levelIndicator =='yellow':
                levels.insert(0,'empty')
                levels.insert(1,'yellow')
                levels.insert(2,'orange')
                levels.insert(3,'red')
            elif levelIndicator =='orange':
                levels.insert(0,'empty')
                levels.insert(1,'empty')
                levels.insert(2,'orange')
                levels.insert(3,'red')
            elif levelIndicator =='red':
                levels.insert(0,'empty')
                levels.insert(1,'empty')
                levels.insert(2,'empty')
                levels.insert(3,'red')
            else:
                levels.insert(0,'empty')
                levels.insert(1,'empty')
                levels.insert(2,'empty')
                levels.insert(3,'empty')

            '''
            print("lamp status ",str(prevLampStatus))
            
            if(levelIndicator == 'red' and not(prevLampStatus)) :
                if(client.publish("lamp", "ON")):
                  prevLampStatus = True
                  print("Light on published successfully")
                else:

                  print("Light on publish Failed")
            elif (levelIndicator == 'green' and prevLampStatus):
                if(client.publish("lamp", "OFF")):
                  print("Light off published successfully")
                else:
                  print("Light off publish Failed")
               
            '''   
            if(levelIndicator == 'red') :
                client.publish("lamp", "ON")
            elif (levelIndicator == 'green' ):
                client.publish("lamp", "OFF")                  


            GPIO.cleanup()

            return json.dumps({'levelIndicator':levelIndicator,'levels':levels})


if __name__ == "__main__":
   app.run(host='0.0.0.0', port=80, debug=True)