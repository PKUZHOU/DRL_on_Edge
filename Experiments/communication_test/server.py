import socket,struct,os
import threading
import time
import cv2
import numpy as np
import json

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind(('192.168.1.18',8888))
s.listen(5)

print('Waiting for connection')
total_thread = 0

def tcplink(sock, addr):
    print('Accept new connection from %s: %s...' %addr)
    sock.send('Welcome!')
    global total_thread
    window = 'agent'+str(total_thread)
    total_thread += 1
    while True:
        full_file = ''
        size = struct.calcsize('128s1')
        buf = sock.recv(size)
        if buf:
            total_len = struct.unpack('128s1',buf)
        receive_len = 0
        while receive_len<int(total_len[0][:5])-1024:
            #print(receive_len)
            rdata = sock.recv(1024)
            receive_len+=1024
            full_file+=rdata
        rdata = sock.recv(int(total_len[0][:5]) - receive_len)
        full_file+=rdata
        mat = json.loads(full_file)
        mat = np.asarray(mat,dtype=np.int8)
        cv2.imshow(window,mat)
        cv2.waitKey(1)

while True:
    sock,addr = s.accept()
    t = threading.Thread(target=tcplink,args=(sock,addr))
    t.start()