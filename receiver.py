# reciever data structure: s|time|temp|hum|pres|gps_lon|gps_lat|gps_alt|
import glob
import io
import time
import json
from dbm.dumb import error
from threading import Thread
import os

from config import input_filepath

imageBytes = b''

from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True # Allow to safe bad images

def wait_for_data(webserver_queue, message_queue):
    lastProcessed = 1
    #exit()
    while True:
        if os.path.isfile(input_filepath + "/" + str(lastProcessed) + ".bin"):
            filename = input_filepath + "/" + str(lastProcessed) + ".bin"
            lastProcessed += 1
            #print(filename)

            f = open(filename, "rb")

            input_raw_data = f.read()

            f.close()
           # print(input_raw_data)

            if input_raw_data[0] == 118:  # test for v character at beginning (Image Data)
                #print("Image Data")
                #print(input_raw_data)
                handle_image(input_raw_data[1:], False, webserver_queue, message_queue)

            elif input_raw_data[0] == 115:  # test for s character at begingin (Sensor Data)
                #print("Sensor Data")
                #print(input_raw_data)
                try:
                    input_data = input_raw_data.decode("utf-8")
                except:
                    message_queue.put("Fehler beim verarbeiten der Daten")
                    print("DATA Error")
                else:
                    handle_sensor(input_data, webserver_queue, message_queue)

            elif input_raw_data[0] == 120:  # test for x character at beginning (last Image Data)F
                #print("last Image Data")
                #print(input_raw_data)
                handle_image(input_raw_data[2:input_raw_data[1]], True, webserver_queue, message_queue)


        #processed_files.add(file)

        # Pause zwischen den Überprüfungen
          # Überprüft alle 5 Sekunden
        time.sleep(0.01)
        #print("waiting...")





def handle_sensor(input_data, webserver_queue, message_queue):
    try:
        data = input_data.split("|")

        errorPacket = data[17]
        for i in range(0, len(errorPacket), 6):
            if errorPacket[i] == "E":
                message_queue.put(errorPacket[i:i+6])
            else:
                break

        with open("data.json", 'r') as file:
            json_data = json.load(file)

        json_block = {"send_time": float(data[1]), "receive_time": time.time(), "temperature": string_to_float(data[2]),
                      "humidity": string_to_float(data[3]), "pressure": string_to_float(data[4]),
                      "gps_lon": string_to_float(data[9]), "gps_lat": string_to_float(data[10]), "gps_alt": string_to_float(data[8]), "gps_sat": string_to_float(data[11]), "gps_speed": string_to_float(data[12]), "magnetic_lon": string_to_float(data[5]), "magnetic_lat": string_to_float(data[6]), "magnetic_alt": string_to_float(data[7]), "co2": string_to_float(data[13]), "TVOC": string_to_float(data[14]), "imageSent": string_to_float(data[15]), "imageFull": string_to_float(data[16])}

        webserver_queue.put(json_block)

        json_data['data'].append(json_block)

        with open("data.json", 'w') as file:
            json.dump(json_data, file, indent=4)
    except:
        message_queue.put("Fehler beim verarbeiten der Daten")
        print("DATA Error")


def handle_image(input_data, last_data_block, webserver_queue, message_queue):
    global imageBytes
    imageBytes += bytes(input_data)
    if last_data_block:
        #print(imageBytes)
        image_time = str(int(time.time()))
        handle_image_thread = Thread(target=build_image, args=(imageBytes, image_time, webserver_queue, message_queue,))
        handle_image_thread.daemon = False
        handle_image_thread.start()
        imageBytes = b''


def build_image(imageBytes, image_time, webserver_queue, message_queue):
    try:
        image_stream = io.BytesIO(imageBytes)
        image = Image.open(image_stream)
        image.save('images/' + image_time + '.jpg')
    except Exception as e:
        print(e)
        print(imageBytes)
        print("Fehler beim verarbeiten eines Bildes")
        message_queue.put("Fehler beim verarbeiten eines Bildes")
    else:
        print("Decoded Image Size:", len(imageBytes))
        print("Image received and saved successfully!")
        webserver_queue.put({"image": image_time + ".jpg"})

def string_to_float(s):
    try:
        return float(s)
    except ValueError:
        return 0.0