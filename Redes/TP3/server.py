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

def printExhibitorIds():
    listIds = []
    for exhibitor in exhibitors:
        listIds.append(exhibitor.getId())
    print("Exhibitors live: ", listIds)
   
def printBroadcasterIds():
    listIds = []
    for broadcaster in broadcasters:
        listIds.append(broadcaster.getId())
    print("Broadcastes live:", listIds)
    
def getPlanetList():
    planetList = []
    for exhibitor in exhibitors:
        planetList.append(exhibitor.getPlanetName())
    for broadcaster in broadcasters:
        planetList.append(broadcaster.getPlanetName())
    return planetList

def printPlanetList():
    print(getPlanetList())
            
def lookupList(elems, id):
    print('looking for id:', id)
    for elem in elems:
        print('actual id:', elem.getId())
        if elem.getId() == id:
            return elem
    print("Couldn't find exhibitor id")
    
def broadcast(message, sender):
    for exhibitorIt in exhibitors:
        if exhibitorIt != sender:
            exhibitorIt.send(message)

# Function to handle clients'connections

def handle_client(client):
    while client.isLive():
        try:
            printExhibitorIds()
            printBroadcasterIds()
            client.printClient()
            message = client.recv(1024)
            print("Trying to eval")
            evalClientMessage(client, message)
            print("Finishing the eval")
        except:
        #    if client.getRole() == 'exhibitor':
        #        exhibitors.remove(client)
        #    elif client.getRole() == 'broadcaster':
        #        broadcasters.remove(client)
                
            client.close()
            break
        
    client.close()
        
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
        planetName = getBufferFromMessage(message)
        client.setPlanetName(planetName)
        print ('< received', planetName, 'from', origin)
        
        return origin, destin, planetName
    else:
        return 0, 0, 0
    
def evalKillClient(client, message):
    broadcaster = lookupList(broadcasters, client.getId())
    exhibitor = lookupList(exhibitors, broadcaster.getExhibitorId())
    
    serverId = server.getId()
    
    destin = getDestinFromMessage(message)
    messageId = server.getIdMessage()
    exhibitor.send(KILL_MESSAGE(serverId, destin, messageId))
    exhibitors.remove(exhibitor)
    exhibitor.killClient()
    exhibitor.close()
    
    origin = getOriginFromMessage(message)
    broadcaster.send(OK_MESSAGE(serverId, origin, messageId))
    broadcasters.remove(broadcaster)
    broadcaster.killClient()
    broadcaster.close()
    
    print('< received kill from', origin)
    
def evalMsgClient(client, message):
    destin = getDestinFromMessage(message)
    bufferSize = getBufferSizeFromMessage(message)
    messageId = server.getIdMessage()
    newMessage = getBufferFromMessage(message)
    
    msg = MSG_MESSAGE(client.getId(), destin, messageId, bufferSize, newMessage)
    
    if destin == 0:
        broadcast(msg, client.getId())
    else:
        destinExhibitor = lookupList(exhibitors, destin)
        destinExhibitor.send(msg)
    
    client.send(OK_MESSAGE(client.getId(), server.getId(), messageId))    
    print("< sent message from", client.getId(), "to", destin)
        
def evalClientMessage(client, message):
    messageId = getTypeFromMessage(message)
    if messageId == messageType["kill"]:
        evalKillClient(client, message)
    elif messageId == messageType["msg"]:
        print("Avaliando mensagem enviada:")
        evalMsgClient(client, message)
            
         
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