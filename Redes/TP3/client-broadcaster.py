#!/usr/bin/env python3

import selectors
import socket
import types

from common import *

import threading
import socket

def client_receive(broadcaster):
    while broadcaster.isLive():
        try:
            message = broadcaster.recv(1024)
            ret  = eval(broadcaster, message)
            if ret == -1:
                break
        except:
            print('Error on recv!')
            broadcaster.close()
            break
        
    broadcaster.close()    
    
def client_send(broadcaster):
        while broadcaster.isLive():
            message = input('')
            newMessage = encodeMessage(broadcaster, message)
            broadcaster.send(newMessage) 

if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit("Usage: python server.py [ip] [port]")
        
    host = sys.argv[1] #'127.0.0.1'
    port = int(sys.argv[2]) #59000

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    broadcaster = Broadcaster(-1, client)
    broadcaster.connect(host, port)

    send_thread = threading.Thread(target=client_send, args=(broadcaster,))
    send_thread.start()

    receive_thread = threading.Thread(target=client_receive, args=(broadcaster,))
    receive_thread.start()