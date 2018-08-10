import socket
import gym
import time
import json
import struct
import cv2
import os
env = gym.make('Breakout-v0')
observation = env.reset()



s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(('192.168.1.18',8888))

# print(s.recv(1024))
# for data in ['a','b','c']:
#     s.send(data)
#     print(s.recv(1024))

def send_mat(s,mat):
    fileinfo_size = struct.calcsize('128s1')
    matlen = len(mat)
    sentlen = 0
    fhead = struct.pack('128s1',str(len(mat)))
    s.send(fhead)
    while matlen-sentlen >1024:
        s.send(mat[sentlen:sentlen+1024])
        sentlen+=1024
    s.send(mat[sentlen:matlen])
    print('send over...')

for _ in range(10000):
    #env.render()
    # print(env.action_space.sample())
    observation, reward, done, info = env.step(env.action_space.sample())
    time.sleep(0.033)
    if (done):
        observation = env.reset()
        observation, reward, done, info = env.step(env.action_space.sample())
    observation = cv2.resize(observation, (84, 84))
    # observation = cv2.resize(observation, (42, 42))
    observation = json.dumps(observation.tolist())
    #

    send_mat(s,observation)
    #print(env.action_space.sample())


s.send('exit')
s.close()

