# Управляем роботом пылесосом Xiaomi Roborock vaccum с помощью веб интерфейса и камеры.
import cv2
import time
import threading
import json
import dload
import urllib.request

from flask import Response
from flask import Flask
from flask import render_template
from flask import request, send_from_directory

import lib.bot_control as botc
# from lib.Battery import Battery as Battery
# from lib.colors import *
# from config import *

Config = None

bot_ip = ''
bot_token = ''
bot_driver = ''

screen_update_frame_rate = -1
capture = None
outputFrame = None
rtsp_link = ''
# rtsp_link = 'rtsp://192.168.1.88:8080/h264_pcm.sdp'
to_min_speed, to_max_speed = -0.3, 0.3
# to_min_angle, to_max_angle = -1.0, 1.0
to_min_angle, to_max_angle = -0.5, 0.5
sequenceId = 1
max_speed = 6

web_server_listen_ip = ''
web_server_listen_port = ''
encode_param = None


def generate_response():
    if outputFrame is None:
        return
    sleep_delay = 1/screen_update_frame_rate
    while True:
        l = outputFrame.__len__()
        if outputFrame is None or l == 0:
            continue
        # scale_percent = 50 # percent of original size
        # width = int(outputFrame.shape[1] * scale_percent / 100)
        # height = int(outputFrame.shape[0] * scale_percent / 100)
        # dim = (width, height)
        # resized = cv2.resize(outputFrame, dim, interpolation = cv2.INTER_AREA)
        (flag, encodedImage) = cv2.imencode(".jpg", outputFrame, encode_param)
        # (flag, encodedImage) = cv2.imencode(".jpg", resized)
        if not flag:
            continue
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
              bytearray(encodedImage) + b'\r\n')
        time.sleep(sleep_delay)


def translate_pad(value, leftMin, leftMax, rightMin, rightMax):
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin
    valueScaled = float(value - leftMin) / float(leftSpan)
    ret_val = rightMin + (valueScaled * rightSpan)
    return ret_val


def move_vacumba(x_change, y_change):
    global sequenceId
    speed_x = translate_pad(x_change, -6, 6, to_min_speed, to_max_speed)
    speed_y = translate_pad(y_change, -6, 6, to_min_angle, to_max_angle)
    if abs(speed_x) < 0.07:
        speed_x = 0
    try:
        if Config["allow_move_bot"]:
            if speed_x != 0 or speed_y != 0:
                botc.move_bot(bot_driver, bot_ip, speed_y,
                              speed_x, 200, sequenceId)
                sequenceId += 1
    except:
        if Config["allow_move_bot"]:
            botc.start_bot(bot_ip)
        pass


def get_vacumba_status():
    global VacumbaStatus
    while True:
        status_url = "http://%s/api/current_status" % ip
        response = urllib.request.urlopen(status_url)
        vacumba_status = response.read()
        VacumbaStatus = json.loads(vacumba_status)
        output = open("./simple_map_drawer_js/status.json", 'wb')
        output.write(vacumba_status)
        output.close()
        time.sleep(1)


def poll_map(ip):
    status_url = "http://%s/api/poll_map" % ip
    response = urllib.request.urlopen(status_url)
    vacumba_status = response.read()
    poll_res = json.loads(vacumba_status)


def update_map(ip):
    while True:
        poll_map(ip)
        map_url = "http://%s/api/map/latest" % ip
        dload.save(map_url, "./templates/dist/latest", True)
        time.sleep(1.5)


web_server = Flask(__name__)


@web_server.route("/")
def index():
    return render_template("index.html")


@web_server.route('/dist/<path:path>')
def send_js(path):
    return send_from_directory('templates/dist', path)


@web_server.route('/simple_map_drawer_js/<path:path>')
def send_map(path):
    return send_from_directory('simple_map_drawer_js/', path)


@web_server.route("/video_feed")
def video_feed():
    return Response(generate_response(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


@web_server.route('/move_pad', methods=['POST'])
def get_post_javascript_data_pad():
    global x_change, y_change
    jsdata = request.form['pad_data']
    pad_data = json.loads(jsdata)
    pad_data['frontPosition']['y'] = -pad_data['frontPosition']['y']
    pad_data['frontPosition']['x'] = -pad_data['frontPosition']['x']
    x_change = translate_pad(pad_data['frontPosition']['y'], -100, 100, -6, 6)
    y_change = translate_pad(pad_data['frontPosition']['x'], -100, 100, -6, 6)
    move_vacumba(x_change, y_change)
    return jsdata


@web_server.route('/action', methods=['POST'])
def get_post_javascript_data_action():
    jsdata = request.form['action']
    if jsdata == 'start_bot':
        print('start')
        botc.start_bot(bot_ip)
    if jsdata == 'stop_bot':
        print('stop')
        botc.stop_bot(bot_ip)
    if jsdata == 'home_bot':
        botc.bot_home(bot_ip)
        print('home')

    return jsdata


def update():
    global capture, outputFrame
    # Read the next frame from the stream in a different thread
    while True:
        if capture.isOpened():
            (status, frame) = capture.read()
            if status == True:
                outputFrame = frame.copy()
            else:
                check = False
                while not check:
                    capture = cv2.VideoCapture(rtsp_link)
                    (status, frame) = capture.read()
                    if status:
                        check = True
                    else:
                        time.sleep(0.2)


def run_server():
    web_server.run(host=web_server_listen_ip, port=web_server_listen_port,
                   debug=Config["web_server_debug"], threaded=True, use_reloader=False)


if __name__ == '__main__':
    with open('config.json') as json_file:
        Config = json.load(json_file)
    bot_ip = Config["bot_ip"]
    bot_token = Config["bot_token"]
    bot_driver = Config["bot_driver"]
    screen_update_frame_rate = Config["screen_update_frame_rate"]
    rtsp_link = Config["rtsp_link"]
    web_server_listen_ip = Config["web_server_listen_ip"]
    web_server_listen_port = Config["web_server_listen_port"]
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), Config["mjpeg_quality"]]
    capture = cv2.VideoCapture(rtsp_link)
    web_server_thread = threading.Thread(target=run_server)
    web_server_thread.start()
    frame_update_thread = threading.Thread(target=update, args=())
    frame_update_thread.start()

    map_update_thread = threading.Thread(
        target=update_map, args=[Config["bot_ip"]])
    map_update_thread.start()
    input("Press any key to exit...")
