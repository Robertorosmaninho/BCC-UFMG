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
    
def broadcast(message, sender):
    for exhibitorIt in server.getExhibitors():
        if exhibitorIt != sender:
            exhibitorIt.send(message)

# Function to handle clients'connections

def handle_client(client):
    while client.isLive():
        try:
            #server.printExhibitorIds()
            #server.printBroadcasterIds()
            #client.printClient()
            message = client.recv(1024)
            #print("Trying to eval")
            evalClientMessage(client, message)
            #print("Finishing the eval")
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
        server.addExhibitor(exhibitor)
        return exhibitor
    else:
        newOrigin = server.getBroadcasterCounter()
        broadcaster = Broadcaster(newOrigin, client)
        if isExhibitor(previousOrigin):
            broadcaster.setExhibitor(previousOrigin)
            exhibitor = lookupList(server.getExhibitors(), previousOrigin)
            if exhibitor is None:
                broadcaster.send(ERROR_MESSAGE(server.getId(), newOrigin, 
                                               server.getIdMessage()))
                print("< error trying to sync to non existent exhibitor")
                return broadcaster    
            exhibitor.setBroadcaster(previousOrigin)
            #broadcaster.printClient()
        server.addBroadcaster(broadcaster)  
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
    broadcaster = lookupList(server.getBroadcasters(), client.getId())
    exhibitor = lookupList(server.getExhibitors(), broadcaster.getExhibitorId())
    
    if broadcaster is None or exhibitor is None:
        client.send(ERROR_MESSAGE(server.getId(), client.getId(), 
                                  server.getIdMessage()))
        print("< error trying to kill a non existent client")
    
    serverId = server.getId()
    
    destin = getDestinFromMessage(message)
    messageId = getMessageIdFromMessage(message)
    exhibitor.send(KILL_MESSAGE(serverId, destin, messageId))
    server.removeExhibitor(exhibitor)
    exhibitor.killClient()
    exhibitor.close()
    
    origin = getOriginFromMessage(message)
    broadcaster.send(OK_MESSAGE(serverId, origin, messageId))
    server.removeBroadcaster(broadcaster)
    broadcaster.killClient()
    broadcaster.close()
    
    print('< received kill from', origin)
    
def evalMsgClient(client, message):
    #print("descobrindo destino da msg")
    destin = getDestinFromMessage(message)
    #print("descobrindo bufferSize da msg")
    bufferSize = getBufferSizeFromMessage(message)
    #print("descobrindo messageId da msg")
    messageId = getMessageIdFromMessage(message)
    #print("descobrindo o buffer da msg")
    newMessage = getBufferFromMessage(message)
    
    #print("pegou todos os dados necessarios para construir a msg")
    msg = MSG_MESSAGE(client.getId(), destin, messageId, bufferSize, newMessage)
    
    #print("Construiu a msg")
    if destin == 0:
        broadcast(msg, client.getId())
    else:
        destinExhibitor = lookupList(server.getExhibitors(), destin)
        #print("procurou o exibidor")
        if destinExhibitor is None:
            #print("Não achou o exibidor")
            client.send(ERROR_MESSAGE(server.getId(), client.getId(), messageId))
            print("< error trying to send message to a non existent exhibitor")
            return
        #print("achou o exibidor")
        destinExhibitor.send(msg)
        #print("eviou msg para o exibidor")
    client.send(OK_MESSAGE(client.getId(), server.getId(), messageId))    
    print("< sent message from", client.getId(), "to", destin)
    
    
def evalCreqClient(client, message):
    destin = getDestinFromMessage(message)
    messageId = getMessageIdFromMessage(message)
    
    destinExhibitor = lookupList(server.getExhibitors(), destin)
    if destinExhibitor is None:
        client.send(ERROR_MESSAGE(server.getId(), client.getId(), messageId))
        print("< error trying to send a clist to a non existent exhibitor")
        return
    
    ids = ""
    for id in server.getClientsIds():
        ids += str(id) + " "
    clist = "clist: \"" + ids[:-1] + "\""
    clistSize = len(clist)
    
    #print("enviando msg para o exibidor")
    destinExhibitor.send(CLIST_MESSAGE(server.getId(), client.getId(), 
                                        messageId, clistSize, clist))
    #print("eviou msg para o exibidor")
    client.send(OK_MESSAGE(server.getId(), client.getId(), messageId))
    #print("enviou msg pro emissor")
    print("< received creq from", client.getId(), "to", destin)

def evalPlanetClient(client, message):
    destin = getDestinFromMessage(message)
    messageId = getMessageIdFromMessage(message)
    
    destinExhibitor = lookupList(server.getExhibitors(), destin)
    if destinExhibitor is None:
        client.send(ERROR_MESSAGE(server.getId(), client.getId(), messageId))
        print("< error trying to discover the planet of non existent exhibitor")
        return
    destinExhibitor.send(PLANET_MESSAGE(client.getId(), destin, messageId))
    client.send(OK_MESSAGE(server.getId(), client.getId(), messageId))
    
        
def evalPlanetListClient(client, message):
    destin = getDestinFromMessage(message)
    messageId = getMessageIdFromMessage(message)
    
    destinExhibitor = lookupList(server.getExhibitors(), destin)
    if destinExhibitor is None:
        client.send(ERROR_MESSAGE(server.getId(), client.getId(), messageId))
        print("< error trying to send the planetlist to a non existent exhibitor")
        return
    
    planets = ""
    for planet in server.getPlanetList():
        planets += planet + " "
    planetList =  "planetlist: \"" + planets[:-1] + "\""
    planetListSize = len(planetList)
    
    destinExhibitor.send(PLANETLIST_RESP_MESSAGE(client.getId(), destin, messageId, 
                                            planetListSize, planetList))
    client.send(OK_MESSAGE(server.getId(), client.getId(), messageId))
    
        
def evalClientMessage(client, message):
    messageId = getTypeFromMessage(message)
    if messageId == messageType["kill"]:
        evalKillClient(client, message)
    elif messageId == messageType["msg"]:
        evalMsgClient(client, message)
    elif messageId == messageType["creq"]:
        evalCreqClient(client, message)
    elif messageId == messageType["planet"]:
        evalPlanetClient(client, message)
    elif messageId == messageType["planetlist"]:
        evalPlanetListClient(client, message)
    
         
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
        #newClient.printClient()
        thread.start()


if __name__ == "__main__":
    receive(host, port)