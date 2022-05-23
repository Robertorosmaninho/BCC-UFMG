#!/usr/bin/env python3

from base64 import encode
import socket
import sys
from common import *
from libServer import *
import threading
import socket
    
def evalClientMessage(client, message):
    messageId = int(decodeMessage(message, "type"))
    if messageId == messageType["hi"]:
        return evalHiClient(client, message)
    elif messageId == messageType["origin"]:
        evalOriginClient(client, message)
    elif messageId == messageType["kill"]:
        evalKillClient(client, message)
    elif messageId == messageType["msg"]:
        evalMsgClient(client, message)
    elif messageId == messageType["creq"]:
        evalCreqClient(client, message)
    elif messageId == messageType["planet"]:
        evalPlanetClient(client, message)
    elif messageId == messageType["planetlist"]:
        evalPlanetListClient(client, message)
    elif messageId == messageType["ok"]:
        evalOkClient(message)
    else:
        print("error to eval messagem from client to server")
        print("received message was: " + message)

# Function to handle clients'connections
def handle_client(client):
    while client.isLive():
        try:
            message = client.recv(1024)
            evalClientMessage(client, message)
        except:                
            client.close()
            break
        
    client.close()
         
# Main function to receive the clients connection
def receive(host, port):
     server.connect(host,port)
     
     print('< initialized server with id', server.getId())
     while True:
        client, _ = server.accept()

        # Recebendo o hi
        try:
            hiMessage = client.recv(1024)
            newClient = evalHiClient(hiMessage, client)
        except:
            print('Error on hi recv/send')
            server.close()
            break
        
        thread = threading.Thread(target=handle_client, args=(newClient,))
        thread.start()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("Usage: python server.py [ip] [port]")
    
    host = sys.argv[1] #'127.0.0.1'
    port = int(sys.argv[2]) #59000
    receive(host, port)