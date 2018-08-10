import socket
import gym
import time
import json
import struct
import cv2
import numpy as np
import os

Game = "Breakout-v0"
Server_ip = '222.29.97.61'
Server_port = 8888
window_size = 84
fps_time = 1./30
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

def get_action(s):
    action = int(s.recv(1))
    # print('action : ', action)
    return action
#    testmat+=mat[sentlen:matlen]
#    testmat = json.loads(testmat)
#    testmat = np.asarray(testmat,dtype=np.int8)
#    cv2.imshow('test',testmat)
#    cv2.waitKey(1)

for _ in range(Total_frames):

    # observation, reward, done, info = env.step(2)
    start = time.time()
    action = get_action(s)
    print "latency_get_action\t "+str(time.time() - start)

    start = time.time()
    observation, reward, done, info = env.step(action)
    #time.sleep(fps_time)
    if (done):
        observation = env.reset()
        observation, reward, done, info = env.step(env.action_space.sample())
    observation = cv2.resize(observation, (window_size, window_size))
    print "time render\t"+str(time.time()-start)

    start = time.time()
    observation = json.dumps(observation.tolist())
    send_mat(s,observation)
    print "send \t"+str(time.time()-start)


s.send('exit')
s.close()

