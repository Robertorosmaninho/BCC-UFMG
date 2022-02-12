#!/usr/bin/env python3

from base64 import encode
import socket
import sys

from common import *

'Chat Room Connection - Client-To-Client'
import threading
import socket

host = '127.0.0.1'
port = 59000

exhibitors = []
broadcasters = []

def lookupList(elems, id):
    print('looking for id:', id)
    for elem in elems:
        print('actual id:', elem.getId())
        if elem.getId() == id:
            return elem
    print("Couldn't find exhibitor id")
    
def broadcast(message, exhibitor):
    for exhibitorIt in exhibitors:
        if exhibitorIt != exhibitor:
            exhibitorIt.send(message)

# Function to handle clients'connections

def handle_client(client):
    while True:
        try:
            message = client.recv(1024)
            client.printClient()
            evalClientMessage(client, message)
            #broadcast(message, client)
        except:
            if client.getRole() == 'exhibitor':
                exhibitors.remove(client.getId())
            elif client.getRole() == 'broadcaster':
                broadcasters.remove(client.getId())
                
            client.close()
            break
        
def isExhibitor(id):
    return id >= rangeIdExhibitor[0] and id <= rangeIdExhibitor[1]

def getNewOrigin(previousOrigin, client):
    newOrigin = 0
    if previousOrigin == defaultIdExhibitor:
        newOrigin = server.getExhibitorCounter() 
        exhibitor = Exhibitor(newOrigin, client)
        exhibitors.append(exhibitor)
        return exhibitor
    else:
        newOrigin = server.getBroadcasterCounter()
        broadcaster = Broadcaster(newOrigin, client)
        print('passou aqui -> broadcast')
        if isExhibitor(previousOrigin):
            print('passou aqui -> broadcast com exhibitor')
            broadcaster.setExhibitor(previousOrigin)
            exhibitor = lookupList(exhibitors, previousOrigin)    
            exhibitor.setBroadcaster(previousOrigin)
            exhibitors.append(exhibitor)
            broadcaster.printClient()
        broadcasters.append(broadcaster)  
        return broadcaster    
    
def evalHiClient(message, client):
    if getTypeFromMessage(message) == messageType["hi"]:
        print('< received hi')
        previousOrigin = getOriginFromMessage(message)
        newClient = getNewOrigin(previousOrigin, client)
        return newClient
    else:
         sys.exit('[HI] Error format')

def evalOriginClient(client, message):
    if getTypeFromMessage(message) == messageType["origin"]:
        origin = getOriginFromMessage(message)
        destin = server.getId() 
        planetName = getPlanetNameFromOriginMessage(client, message)
        client.setPlanetName(planetName)
        print ('< received', planetName, 'from', origin)
        
        return origin, destin, planetName
    else:
        return 0, 0, 0
    
def evalKillClient(client, message):
    broadcaster = lookupList(broadcasters, client.getId())
    exhibitor = lookupList(exhibitors, broadcaster.getExhibitorId())
    
    
    serverId = server.getId()
    messageId = server.getIdMessage()
    exhibitor.send(KILL_MESSAGE(serverId, destin, messageId))
    exhibitor.close()
    broadcaster.send(OK_MESSAGE(serverId, origin, messageId))
    broadcaster.close()
    print('< received kill from', origin)
        
def evalClientMessage(client, message):
    messageId = getTypeFromMessage(message)
    if messageId == messageType["kill"]:
        evalKillClient(client, message)
            
         
# Main function to receive the clients connection
def receive(host, port):
     server.connect(host,port)
     
     print('< initialized server with id', server.getId())
     while True:
        client, address = server.accept()

        # Recebendo o hi
        try:
            hi_client = client.recv(1024)
            newClient = evalHiClient(hi_client, client)
            server.registerNewClient(newClient)
            newClient.send(OK_MESSAGE(server.getId(), newClient.getId(), 
                                   server.getIdMessage()))
        except:
            print('Error on hi recv/send')
            server.close()
            break
        
        # Recebendo o origin
        try:
            origin_client = newClient.recv(1024)
            origin, destin, planetName = evalOriginClient(newClient, origin_client)
            newClient.send(OK_MESSAGE(origin, destin, server.getIncIdMessage()))
        except:
            print('Error on origin recv/send')
            server.close()
            break
        
        thread = threading.Thread(target=handle_client, args=(newClient,))
        newClient.printClient()
        thread.start()


if __name__ == "__main__":
    receive(host, port)