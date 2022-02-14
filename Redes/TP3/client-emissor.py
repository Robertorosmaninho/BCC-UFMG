#!/usr/bin/env python3

import selectors
import socket
import types

from common import *
#  HI_MESSAGE(defaultIdExibidor, defaultIdEmissor, idMensagem)

import threading
import socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = '127.0.0.1'
port = 59000

broadcaster = Broadcaster(-1, client)
broadcaster.connect(host, port)

def client_receive():
    while broadcaster.isLive():
        #try:
       message = broadcaster.recv(1024)
       ret  = eval(broadcaster, message)
       if ret == -1:
            break
        #except:
        #    print('Error on recv!')
        #    broadcaster.close()
        #    break
        
    broadcaster.close()     


def client_send():
    while broadcaster.isLive():
        message = input('')
        newMessage = encodeMessage(broadcaster, message)
        broadcaster.send(newMessage)

send_thread = threading.Thread(target=client_send)
send_thread.start()

receive_thread = threading.Thread(target=client_receive)
receive_thread.start()