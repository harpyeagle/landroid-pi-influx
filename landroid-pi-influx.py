import time as t
import datetime
import math
import picamera
from PIL import Image
import numpy as np

from landroidcc import Landroid

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# LANDROID WORX LOGIN DETAILS
landroid = Landroid()
landroid.connect("<YOUR-USERNAME>", "<YOUR-PASSWORD>")


# INFLUXDB TOKEN TO THE BUCKET
token = "<YOUR-INFLUXDB-TOKEN>"
org = "yourorg"
bucket = "worx"
client = InfluxDBClient(url="http://<YOUR-URL>:8086", token=token)
write_api = client.write_api(write_options=SYNCHRONOUS)


# TAKE A PICTURE FOR EACH 10 MIN BLOCK IN THE HOUR - TIMESTAMP THE PICTURE
def get_image():
        camera = picamera.PiCamera(resolution=(640, 480))
        camera.rotation = 180
        t.sleep(2) 
        camera.annotate_background = picamera.Color('black')
        camera.annotate_text = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        imgnm = str(math.floor(int(datetime.datetime.now().strftime('%M'))/10))
        camera.capture(f'/home/pi/<YOUR-DIR>/img{imgnm}.jpg')
        camera.close()

# USING LANDROIDCC GET THE STATUS 

def get_data():

        status = landroid.get_status()

        bstate = str(status.get_state())
        berror = str(status.get_error())
        bpercent = int(status.get_battery().percent)
        bcharges = int(status.get_battery().charges)
        bvolts = float(status.get_battery().volts)
        btemperature = float(status.get_battery().temperature)
        bcharging = str(status.get_battery().charging)

        return (bpercent, btemperature, bvolts, bstate, berror, bcharging)

# USING PILLOW AND NUMPY TO CONCAT THE IMAGES  
def con_image():

        s0 = np.asarray(Image.open('/home/pi/<YOUR-DIR>/img0.jpg'))
        s1 = np.asarray(Image.open('/home/pi/<YOUR-DIR>/img1.jpg'))
        s2 = np.asarray(Image.open('/home/pi/<YOUR-DIR>/img2.jpg'))
        s3 = np.asarray(Image.open('/home/pi/<YOUR-DIR>/img3.jpg'))
        s4 = np.asarray(Image.open('/home/pi/<YOUR-DIR>/img4.jpg'))
        s5 = np.asarray(Image.open('/home/pi/<YOUR-DIR>/img5.jpg'))

        stepsall = np.concatenate((s0, s1, s2, s3, s4, s5), axis=1)

        im = Image.fromarray(stepsall)
        im.save('/home/pi/<YOUR-DIR>/influx-worx.jpg')
        

#CAPTURE THE DATA EVERY 5 MIN - MORE FREQUENT AND THE WORX CLOUD MAY HAVE ISSUES
while True:
        try:
                bpercent, btemperature, bvolts, bstate, berror, bcharging = get_data()
                data = f'bpercent,host=wx01 percent={bpercent}\nbtemperature,host=wx01 celsius={btemperature}\nbvolts,host=wx01 volts={bvolts}\nbstate,host=wx01 state="{bstate}"\nberror,host=wx01 error="{berror}"\nbcharging,host=wx01 charging="{bcharging}"'
                write_api.write(bucket, org, data)
                get_image()
                con_image()

        except (KeyboardInterrupt, SystemExit):
                raise
        except:
                pass

        t.sleep(300)
