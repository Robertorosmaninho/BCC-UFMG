from common import *

def broadcast(message, sender):
    for exhibitorIt in server.getExhibitors():
        if exhibitorIt.getId() != sender:
            exhibitorIt.send(message)

def isExhibitor(id):
    return id >= rangeIdExhibitor[0] and id <= rangeIdExhibitor[1]

def registerNewClient(previousOrigin, client):
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
            broadcaster.setExhibitorId(previousOrigin)
            exhibitor = lookupList(server.getExhibitors(), previousOrigin)
            if exhibitor is None:
                broadcaster.send(ERROR_MESSAGE(server.getId(), newOrigin, 
                                               server.getIdMessage()))
                print("< error trying to sync to non existent exhibitor")
                return broadcaster    
            exhibitor.setBroadcasterId(previousOrigin)
        server.addBroadcaster(broadcaster)  
        return broadcaster    
    
def evalHiClient(message, client):
        print('< received hi')
        previousOrigin = int(decodeMessage(message, "origin"))
        newClient = registerNewClient(previousOrigin, client)
        newClient.send(OK_MESSAGE(server.getId(), newClient.getId(), 
                                    server.getIdMessage()))
        return newClient

def evalOriginClient(client, message):
        origin = int(decodeMessage(message, "origin"))
        destin = server.getId() 
        planetName = decodeMessage(message, "buffer")
        client.setPlanetName(planetName)
        print ('< received', planetName, 'from', origin)
        client.send(OK_MESSAGE(origin, destin, server.getIncIdMessage()))
    
def evalKillClient(client, message):
    broadcaster = lookupList(server.getBroadcasters(), client.getId())
    origin = int(decodeMessage(message, "origin"))
    messageId = int(decodeMessage(message, "messageId"))
    serverId = server.getId()
    print('< received kill from', origin)
 
    if client.getExhibitorId() != defaultIdExhibitor:
        exhibitor = lookupList(server.getExhibitors(), broadcaster.getExhibitorId())
    
        if broadcaster is None or exhibitor is None:
            client.send(ERROR_MESSAGE(server.getId(), client.getId(), 
                                      server.getIdMessage()))
            print("< error trying to kill a non existent client")
    
        destin = int(decodeMessage(message, "destin"))
        exhibitor.send(KILL_MESSAGE(serverId, destin, messageId))
        server.removeExhibitor(exhibitor)
        exhibitor.killClient()
        exhibitor.close()
    
    broadcaster.send(OK_MESSAGE(serverId, origin, messageId))
    server.removeBroadcaster(broadcaster)
    broadcaster.killClient()
    broadcaster.close()
    
def evalMsgClient(client, message):
    destin = int(decodeMessage(message, "destin"))
    bufferSize = int(decodeMessage(message, "bufferSize"))
    messageId = int(decodeMessage(message, "messageId"))
    newMessage = decodeMessage(message, "buffer")
    
    msg = MSG_MESSAGE(client.getId(), destin, messageId, bufferSize, newMessage)
    print("< sent message from", client.getId(), "to", destin)
    
    if destin == 0:
        broadcast(msg, client.getId())
    else:
        if not isExhibitor(destin):
            broadcaster = lookupList(server.getBroadcasters(), destin)
            if broadcaster is None:
                client.send(ERROR_MESSAGE(server.getId(), client.getId(), messageId))
                print("< error trying to send message to a non existent broadcaster")
                return
            destin = broadcaster.getExhibitorId()
            
        destinExhibitor = lookupList(server.getExhibitors(), destin)
        if destinExhibitor is None:
            client.send(ERROR_MESSAGE(server.getId(), client.getId(), messageId))
            print("< error trying to send message to a non existent exhibitor")
            return
        destinExhibitor.send(msg)
    client.send(OK_MESSAGE(client.getId(), server.getId(), messageId))
    
def evalCreqClient(client, message):
    destin = int(decodeMessage(message, "destin"))
    messageId = int(decodeMessage(message, "messageId"))
        
    if not isExhibitor(destin):
        broadcaster = lookupList(server.getBroadcasters(), destin)
        if broadcaster is None:
            client.send(ERROR_MESSAGE(server.getId(), client.getId(), messageId))
            print("< error trying to send message to a non existent broadcaster")
            return
        destin = broadcaster.getExhibitorId()     
    
    destinExhibitor = lookupList(server.getExhibitors(), destin)
    print("< received creq from", client.getId(), "to", destin)
    if destinExhibitor is None:
        client.send(ERROR_MESSAGE(server.getId(), client.getId(), messageId))
        print("< error trying to send a clist to a non existent exhibitor")
        return
    
    ids = ""
    for id in server.getClientsIds():
        ids += str(id) + " "
    clist = "clist: \"" + ids[:-1] + "\""
    clistSize = len(clist)
    
    destinExhibitor.send(CLIST_MESSAGE(server.getId(), client.getId(), 
                                        messageId, clistSize, clist))
    client.send(OK_MESSAGE(server.getId(), client.getId(), messageId))

def evalPlanetClient(client, message):
    destin = int(decodeMessage(message, "destin"))
    messageId = int(decodeMessage(message, "messageId"))
    originalDestin = destin

    print("< received planet from", client.getId(), "to", destin)
    if not isExhibitor(destin):
        broadcaster = lookupList(server.getBroadcasters(), destin)
        if broadcaster is None:
            client.send(ERROR_MESSAGE(server.getId(), client.getId(), messageId))
            print("< error trying to send message to a non existent broadcaster")
            return
        destin = broadcaster.getExhibitorId()
    
    destinExhibitor = lookupList(server.getExhibitors(), destin)
    if destinExhibitor is None:
        client.send(ERROR_MESSAGE(server.getId(), client.getId(), messageId))
        print("< error trying to discover the planet of non existent exhibitor")
        return
    
    planetName = server.getPlanetFromId(originalDestin)
    if planetName == "":
        client.send(ERROR_MESSAGE(server.getId(), client.getId(), messageId))
        print("< error trying to discover the planetName")
        return 
    
    destinExhibitor.send(PLANET_RESP_MESSAGE(client.getId(), originalDestin, 
                                             messageId, len(planetName), 
                                             planetName))
    client.send(OK_MESSAGE(server.getId(), client.getId(), messageId))
    
        
def evalPlanetListClient(client, message):
    messageId = int(decodeMessage(message, "messageId"))
    destin = client.getExhibitorId()
    
    destinExhibitor = lookupList(server.getExhibitors(), destin)
    print("< received planetlist from", client.getId(), "to", destin)
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
    
def evalOkClient(message):
    origin = int(decodeMessage(message, "origin"))
    print("< ok from " + str(origin))