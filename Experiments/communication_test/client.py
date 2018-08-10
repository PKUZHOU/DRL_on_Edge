import socket
import gym
import time
import json
import struct
import cv2
import numpy as np
import os

Game = "Breakout-v0"
Server_ip = '192.168.1.18'
Server_port = 8888
window_size = 84
fps_time = 1./24
Total_frames = 100000
Len_data = 1024
env = gym.make(Game)
observation = env.reset()

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect((Server_ip,Server_port))

def send_mat(s,mat):
    matlen = len(mat)
    testmat = ""
    sentlen = 0
    fhead = struct.pack('128s1',str(len(mat)))
    s.send(fhead)
    while matlen-sentlen >Len_data:
        s.send(mat[sentlen:sentlen+Len_data])
        testmat+=mat[sentlen:sentlen+Len_data]
        sentlen+=Len_data
    s.send(mat[sentlen:matlen])
#    testmat+=mat[sentlen:matlen]
#    testmat = json.loads(testmat)
#    testmat = np.asarray(testmat,dtype=np.int8)
#    cv2.imshow('test',testmat)
#    cv2.waitKey(1)

for _ in range(Total_frames):
    observation, reward, done, info = env.step(env.action_space.sample())
    time.sleep(fps_time)
    if (done):
        observation = env.reset()
        observation, reward, done, info = env.step(env.action_space.sample())
    observation = cv2.resize(observation, (window_size, window_size))
    observation = json.dumps(observation.tolist())
    send_mat(s,observation)
    print("sent "+str(_))

s.send('exit')
s.close()

