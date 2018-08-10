import socket,struct,os
import threading
import time
import cv2
import numpy as np
import json
import random

Game = "Breakout-v0"
Server_ip = '222.29.97.61'
Server_port = 8888

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind((Server_ip,Server_port))
s.listen(5)

print('Waiting for connection')
total_thread = 0
Mats = {}
for i in range(5):
    Mats [str(i)] = None


def show_window():
    global Mats
    while True:
        for i in range(5):
            try:
                cv2.imshow(str(i),Mats[str(i)])
            except:
                pass
        cv2.waitKey(1)

def get_action(state):
    action = random.sample(['0', '1', '2', '3'], 1)
    print(action)
    return action



def tcplink(sock, addr):
    print('Accept new connection from %s: %s...' %addr)
    sock.send('1')
    global total_thread
    my_id = total_thread
    window = 'agent'+str(total_thread)
    print(window)
    total_thread += 1
    while True:
        full_file = ''
        size = struct.calcsize('128s1')
        buf = sock.recv(size)
        if buf:
            total_len = struct.unpack('128s1',buf)
        receive_len = 0
        total_len = int(total_len[0][:5])
        while total_len>0:
            readlen = 1024
            if total_len<receive_len: readlen = total_len
            rdata = sock.recv(readlen)
            receive_len+= len(rdata)
            full_file+=rdata
            total_len-=len(rdata)
        mat = json.loads(full_file)
        mat = np.asarray(mat,dtype=np.int8)
        # global Mats
        # Mats[str(my_id)] = mat
        action = get_action(mat)
        sock.send(action[0])

        # cv2.imshow(window,mat)
        # cv2.waitKey(1)

# t1 = threading.Thread(target=show_window,args=[])
# t1.start()
while True:
    sock,addr = s.accept()
    t = threading.Thread(target=tcplink,args=(sock,addr))
    t.start()
