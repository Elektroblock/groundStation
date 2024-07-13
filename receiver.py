# reciever data structure: s|time|temp|hum|pres|gps_lon|gps_lat|gps_alt|
import glob
import io
import time
import json
from threading import Thread
import os
from PIL import Image

imageBytes = b''


def wait_for_data(receiver_queue, webserver_queue):

    #exit()
    directory = "out"
    for i in range(0, 14071):
        filename = "out/" + "output" + str(i) + ".bin"
        #filename = "bild.bin"
        print(filename)

        f = open(filename, "rb")

        input_raw_data = f.read()
        #if len(input_raw_data) == 0:
            #continue
        f.close()
        #open(filename, "w").close()

        #print(input_raw_data)

        if input_raw_data[0] == 118:  # test for v character at beginning (Image Data)
            print("Image Data")
            handle_image(input_raw_data[1:], False, webserver_queue)

        elif input_raw_data[0] == 115:  # test for s character at begingin (Sensor Data)
            print("Sensor Data")
            handle_sensor(input_raw_data.decode("utf-8"), webserver_queue)

        elif input_raw_data[0] == 120:  # test for x character at beginning (last Image Data)
            print("last Image Data")
            handle_image(input_raw_data[1:], True, webserver_queue)

        #print(input_raw_data[0])


def handle_sensor(input_data, webserver_queue):
    data = input_data.split("|")

    with open("data.json", 'r') as file:
        json_data = json.load(file)

    json_block = {"send_time": float(data[1]), "receive_time": time.time(), "temperature": float(data[2]),
                  "humidity": float(data[3]), "pressure": float(data[4]),
                  "gps_lon": float(data[5]), "gps_lat": float(data[6]), "gps_alt": float(data[7])}

    webserver_queue.put(json_block)

    json_data['data'].append(json_block)

    with open("data.json", 'w') as file:
        json.dump(json_data, file, indent=4)


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
    image.save('webservercontent/images/' + image_time + '.jpg')
    print("Decoded Image Size:", len(imageBytes))
    print("Image received and saved successfully!")
    webserver_queue.put({"image": image_time + ".jpg"})
