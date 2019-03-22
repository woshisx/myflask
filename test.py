import os,re,random,socket
import socket
import random, time, queue
from multiprocessing.managers import BaseManager
from datetime import datetime, timedelta
now = datetime.now()
temp = now + timedelta(hours=10)
delta = temp - now
print(type(delta.seconds))
print(type(str(datetime.now()).split('.')[0]))
print(type(datetime.strptime(u'2019-02-25 15:04:26', "%Y-%m-%d %H:%M:%S")))

# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# # 建立连接:
# s.connect(('www.mixwheel.top', 80))
# s.send(b'GET / HTTP/1.1\r\nHost: www.sina.top/admin/ad\r\nConnection: close\r\n\r\n')
# buffer = []
# while True:
#     # 每次最多接收1k字节:
#     d = s.recv(1024)
#     if d:
#         buffer.append(d)
#     else:
#         break
# data = b''.join(buffer)
# print(data)
