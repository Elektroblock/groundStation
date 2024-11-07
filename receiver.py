# reciever data structure: s|time|temp|hum|pres|gps_lon|gps_lat|gps_alt|
import glob
import io
import time
import json
from threading import Thread
import os

from config import input_filepath

imageBytes = b''

from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True # Allow to safe bad images

def wait_for_data(webserver_queue):
    processed_files = set()
    #exit()
    while True:
        # Liste aller Dateien im Ordner, die auf '.bin' enden
        current_files = [f for f in os.listdir(input_filepath) if f.endswith('.bin')]

        # Dateien nach Zahl im Namen sortieren
        current_files.sort(key=lambda x: int(x.split('.')[0]))
        # Neue Dateien in der richtigen Reihenfolge ausgeben
        for file in current_files:
            if file not in processed_files:

                filename = input_filepath + "/" + file

                print(filename)

                f = open(filename, "rb")

                input_raw_data = f.read()

                f.close()
                print(input_raw_data)

                if input_raw_data[0] == 118:  # test for v character at beginning (Image Data)
                    print("Image Data")
                    handle_image(input_raw_data[1:], False, webserver_queue)

                elif input_raw_data[0] == 115:  # test for s character at begingin (Sensor Data)
                    print("Sensor Data")
                    handle_sensor(input_raw_data.decode("utf-8"), webserver_queue)

                elif input_raw_data[0] == 120:  # test for x character at beginning (last Image Data)F
                    print("last Image Data")
                    handle_image(input_raw_data[1:], True, webserver_queue)


                processed_files.add(file)

        # Pause zwischen den Überprüfungen
        time.sleep(1)  # Überprüft alle 5 Sekunden






def handle_sensor(input_data, webserver_queue):
    try:
        data = input_data.split("|")

        with open("data.json", 'r') as file:
            json_data = json.load(file)

        json_block = {"send_time": float(data[1]), "receive_time": time.time(), "temperature": string_to_float(data[2]),
                      "humidity": string_to_float(data[3]), "pressure": string_to_float(data[4]),
                      "gps_lon": string_to_float(data[9]), "gps_lat": string_to_float(data[10]), "gps_alt": string_to_float(data[8]), "gps_sat": string_to_float(data[11]), "gps_speed": string_to_float(data[12]), "magnetic_lon": string_to_float(data[5]), "magnetic_lat": string_to_float(data[6]), "magnetic_alt": string_to_float(data[7])}

        webserver_queue.put(json_block)

        json_data['data'].append(json_block)

        with open("data.json", 'w') as file:
            json.dump(json_data, file, indent=4)
    except:
        print("DATA Error")


def handle_image(input_data, last_data_block, webserver_queue):
    global imageBytes
    imageBytes += bytes(input_data)
    if last_data_block:
        print(imageBytes)
        image_time = str(int(time.time()))
        handle_image_thread = Thread(target=build_image, args=(imageBytes, image_time, webserver_queue,))
        handle_image_thread.daemon = False
        handle_image_thread.start()
        imageBytes = b''


def build_image(imageBytes, image_time, webserver_queue):
    image_stream = io.BytesIO(imageBytes)
    image = Image.open(image_stream)
    image.save('images/' + image_time + '.jpg')
    print("Decoded Image Size:", len(imageBytes))
    print("Image received and saved successfully!")
    webserver_queue.put({"image": image_time + ".jpg"})

def string_to_float(s):
    try:
        return float(s)
    except ValueError:
        return 0.0