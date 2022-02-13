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

exhibitor = Exhibitor(0, client)
exhibitor.connect(host, port)

def encodeMessage(exhibitor, message):
    messageTokens = message.split(' ')
    if messageTokens[0] == 'hi':
        exhibitor.messageIsHi()
        return HI_MESSAGE(exhibitor.getId(), server.getId(), 
                          server.getIncIdMessage())
    if messageTokens[0] == 'origin':
        planetName = messageTokens[2]
        message = ORIGIN_MESSAGE(exhibitor.getId(), server.getId(), 
                                 server.getIncIdMessage(), messageTokens[1],
                                 planetName)
        return message


def client_thread():
    # Envio do HI
    hiMessage = 'hi'#input('')
    encodedHiMessage = encodeMessage(exhibitor, hiMessage)
    exhibitor.send(encodedHiMessage)
        
    # Recido do OK do HI
    okHiMessage = exhibitor.recv(1024)
    eval(exhibitor, okHiMessage)
    
    # Envio do ORIGIN
    originMessage = 'origin 6 netuno'#input('')
    encodedOriginMessage = encodeMessage(exhibitor, originMessage)
    exhibitor.send(encodedOriginMessage)
        
    # Recido do OK do ORIGIN
    okOriginMessage = exhibitor.recv(1024)
    eval(exhibitor, okOriginMessage)
     
    # Exibição
    while exhibitor.isLive():
        message = exhibitor.recv(1024)
        eval(exhibitor, message)
    
    client.close()
        

main_thread = threading.Thread(target=client_thread)
main_thread.start()
