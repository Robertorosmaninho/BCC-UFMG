#!/usr/bin/env python3

import selectors
import socket
import types

from common import *

import threading
import socket

def receive(exhibitor):
    # Envio do Hi/Origin
    message = input('')
    encodedMessage = encodeMessage(exhibitor, message)
    exhibitor.send(encodedMessage)
        
    # Recibo do OK do Hi/Origin
    okMessage = exhibitor.recv(1024)
    eval(exhibitor, okMessage)
    

def client_thread(exhibitor):
    
    # Recebe e trata o Hi
    receive(exhibitor)
    
    # Recebe e trata o Origin
    receive(exhibitor)
     
    # Exibição
    while exhibitor.isLive():
        message = exhibitor.recv(1024)
        eval(exhibitor, message)
    
    client.close()
    

if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit("Usage: python server.py [ip] [port]")
        
    host = sys.argv[1] #'127.0.0.1'
    port = int(sys.argv[2]) #59000

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    exhibitor = Exhibitor(0, client)
    exhibitor.connect(host, port)

    main_thread = threading.Thread(target=client_thread, args=(exhibitor,))
    main_thread.start()
