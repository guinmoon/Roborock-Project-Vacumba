

# import miio
import requests
from datetime import datetime

headers = {'content-type': 'application/json'}


def move_bot(bot_driver,ip,y_speed,x_speed,move_duration,sequenceId = 0):
    if bot_driver=='valetudo':
        move_bot_direct(ip,y_speed, x_speed, move_duration,sequenceId)
    # if bot_driver=='miio':
    #     bot.manual_control(y_speed, x_speed, move_duration)

def move_bot_direct(ip,y_speed,x_speed,move_duration,sequenceId):
    now = datetime.now()
    body = '{"angle":%.4f,"velocity":%.4f,"duration":%i,"sequenceId":%i}'%(y_speed,x_speed,move_duration,sequenceId)                
    r = requests.put('http://%s/api/set_manual_control'%ip,data= body,headers=headers)
    #print(r)
    # self.sequenceId+=1

def bot_goto(ip,x,y):
    body = '{"x":%i,"y":%i}'%(x,y)                
    r = requests.put('http://%s/api/go_to'%ip,data= body,headers=headers)
    print(body)
    # self.sequenceId+=1

def start_bot(ip):
    silence_bot(ip)
    r = requests.put('http://%s/api/start_manual_control'%ip)
    #print(r)

def stop_bot(ip):
    r = requests.put('http://%s/api/stop_manual_control'%ip)
    #print(r)

def bot_home(ip):
    r = requests.put('http://%s/api/drive_home'%ip)
    #print(r)

def silence_bot(ip):
    now = datetime.now()
    body = '{"speed":1}'
    r = requests.put('http://%s/api/fanspeed'%ip,data= body,headers=headers)
    print(r)
    # self.sequenceId+=1