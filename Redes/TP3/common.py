import socket
import sys
    
def lookupList(elems, id):
    for elem in elems:
        if elem.getId() == id:
            return elem
    return None
          
messageType = { "ok"         : 1 
              , "error"      : 2
              , "hi"         : 3
              , "kill"       : 4
              , "msg"        : 5
              , "creq"       : 6
              , "clist"      : 7
              , "origin"     : 8
              , "planet"     : 9
              , "planetlist" : 10
              }

rangeIdExhibitor = (pow(2,12),pow(2,13)-1)
rangeIdBroadcaster = (1, pow(2,12)-1)

defaultIdExhibitor = 0
defaultIdBroadcaster = -1

def decodeMessage(message, attribute):
    strMessage = message.decode('utf-8')
    listAttributes = strMessage.split("|")
    if  attribute == "type":
        return listAttributes[1]
    elif attribute == "origin":
        return listAttributes[2]
    elif attribute == "destin":
        return listAttributes[3]
    elif attribute == "messageId":
        return listAttributes[4]
    elif attribute == "bufferSize":
        return listAttributes[5]
    elif attribute == "buffer":
        if len(listAttributes) > 6:
            return listAttributes[6][1:int(listAttributes[5])+1]
        else:
            sys.exit("Trying to return Buffer from a message without it.")
    else:
        sys.exit("Trying to decode a message with wrong type.")

def MESSAGE(tipo, orig, dest, idMessage):
    message = "| " + str(tipo) + " | " + str(orig) + " | "+ str(dest) + " | " + str(idMessage) + " |"
    return message.encode('UTF-8')
    
def EXT_MESSAGE(tipo, orig, dest, idMessage, bufferSize, buffer):
    oldMessage = MESSAGE(tipo, orig, dest, idMessage)
    newMessage = oldMessage.decode('UTF-8')
    newMessage += ' ' + str(bufferSize) + ' | '+ str(buffer) + ' |'
    return newMessage.encode('utf-8')

def OK_MESSAGE(orig, dest, idMessage):
    return MESSAGE(messageType["ok"], orig, dest, idMessage)

def ERROR_MESSAGE(orig, dest, idMessage):
    return MESSAGE(messageType["error"], orig, dest, idMessage)
    
def HI_MESSAGE(orig, dest, idMessage):
    return MESSAGE(messageType["hi"], orig, dest, idMessage)

def KILL_MESSAGE(orig, dest, idMessage):
    return MESSAGE(messageType["kill"], orig, dest, idMessage)

def ORIGIN_MESSAGE(orig, dest, idMessage, bufferSize, planetName):
    return EXT_MESSAGE(messageType["origin"], orig, dest, idMessage, bufferSize, 
                       planetName)
    
def MSG_MESSAGE(orig, dest, idMessage, bufferSize, message):
    return EXT_MESSAGE(messageType["msg"], orig, dest, idMessage, bufferSize, 
                       message)

def CREQ_MESSAGE(orig, dest, idMessage):
    return MESSAGE(messageType["creq"], orig, dest, idMessage)

def CLIST_MESSAGE(orig, dest, idMessage, bufferSize, clist):
    return EXT_MESSAGE(messageType["clist"], orig, dest, idMessage, bufferSize, 
                       clist)

def PLANET_MESSAGE(orig, dest, idMessage):
    return MESSAGE(messageType["planet"], orig, dest, idMessage)

def PLANETLIST_MESSAGE(orig, dest, idMessage):
    return MESSAGE(messageType["planetlist"], orig, dest, idMessage)

def PLANETLIST_RESP_MESSAGE(orig, dest, idMessage, bufferSize, planetList):
    return EXT_MESSAGE(messageType["planetlist"], orig, dest, idMessage, 
                       bufferSize, planetList)

class Server: 
    def __init__(self):
        self.id = (pow(2, 16) - 1)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.idMessage = 0
        self.exhibitorCounter = rangeIdExhibitor[0] - 1
        self.broadcasterCounter = rangeIdBroadcaster[0] - 1
        self.broadcasters = []
        self.exhibitors = []
        
    def connect(self, host, port):
        self.socket.bind((host, port))
        self.socket.listen()
        
    def getIncIdMessage(self):
        self.idMessage += 1
        return self.idMessage
    
    def getIdMessage(self):
        return self.idMessage
    
    def getExhibitorCounter(self):
        self.exhibitorCounter += 1
        return self.exhibitorCounter
    
    def getBroadcasterCounter(self):
        self.broadcasterCounter += 1
        return self.broadcasterCounter
    
    def registerNewClient(self, client):
        self.clients.add(client)
        
    def accept(self):
        return self.socket.accept()
    
    def close(self):
        return self.socket.close()
        
    def getId(self):
        return self.id
    
    def getBroadcasters(self):
        return self.broadcasters
    
    def getExhibitors(self):
        return self.exhibitors
    
    def addBroadcaster(self, broadcaster):
        self.broadcasters.append(broadcaster)
    
    def removeBroadcaster(self, broadcaster):
        self.broadcasters.remove(broadcaster)
        
    def addExhibitor(self, exhibitor):
        self.exhibitors.append(exhibitor)
        
    def removeExhibitor(self,exhibitor):
        self.exhibitors.remove(exhibitor)
    
    def getClients(self):
        return self.exhibitors + self.broadcasters

    def getPlanetList(self):
        planetList = []
        for client in self.getClients():
            planetList.append(client.getPlanetName())
        return planetList

    def getClientsIds(self):
        listIds = []
        for client in self.getClients():
            listIds.append(client.getId())
        return listIds    
   
server = Server()     

class Client:
    def __init__(self, idClient, socketClient):
        self.id = idClient
        self.socket = socketClient
        self.planetName = ""
        self.Hi = False
        self.live = True
        self.role = ""
        
    def getId(self):
        return self.id
    
    def setId(self, newId):
        self.id = newId
    
    def connect(self, host, port):
        self.socket.connect((host, port))
        
    def send(self, message):
        self.socket.send(message)
        
    def close(self):
        self.socket.close()
        
    def recv(self, buffSize):
        return self.socket.recv(buffSize)
        
    def messageIsHi(self):
        self.Hi = True
        
    def messageIsNotHi(self):
        self.Hi = False
        
    def lastMessageWasHi(self):
        return self.Hi
    
    def isLive(self):
        return self.live
    
    def killClient(self):
        self.live = False
        
    def getRole(self):
        return self.role
    
    def setPlanetName(self, name):
        self.planetName = name
        
    def getPlanetName(self):
        return self.planetName

class Broadcaster(Client):
    def __init__(self, id, socket):
        Client.__init__(self, id, socket)
        self.exhibitorId = defaultIdExhibitor
        self.role = "broadcaster"
        
    def setExhibitorId(self, exhibitor):
        self.exhibitorId = exhibitor
        
    def getExhibitorId(self):
        return self.exhibitorId
    
class Exhibitor(Client):
    def __init__(self, id, socket):
        Client.__init__(self, id, socket)
        self.broadcasterId = defaultIdBroadcaster
        self.role = "exhibitor"
        
    def setBroadcasterId(self, broadcaster):
        self.broadcasterId = broadcaster
        
    def getBroadcasterId(self):
        return self.broadcasterId

def eval(client, message):
    if len(message) == 0:
        return 1
    
    type = int(decodeMessage(message, "type"))
    if type == messageType["ok"]:
        if client.lastMessageWasHi():
            client.messageIsNotHi()
            destin = decodeMessage(message, "destin")
            client.setId(int(destin))
            print("< ok" + destin)
        elif not client.isLive():
            print("< ok")
            client.killClient()
            client.close()
            return -1
        else:
            print("< ok")
            return 0
    elif type == messageType["kill"]:
        print("< kill")
        client.send(OK_MESSAGE(client.getId(), server.getId(), 
                               int(decodeMessage(message, "messageId"))))
        client.killClient()
        client.close()
        return -1 
    elif type == messageType["error"]:
        print("< error")
    elif type == messageType["msg"]:
        origin = int(decodeMessage(message, "origin"))
        messageRecieved = decodeMessage(message, "buffer")
        print('< msg from ' + str(origin) + ': ' + '\"' + str(messageRecieved) +  '\"')   
        client.send(OK_MESSAGE(client.getId(), server.getId(), 
                               int(decodeMessage(message, "messageId"))))
    elif type == messageType["clist"]:
        clist = decodeMessage(message, "buffer")
        print(clist)
        client.send(OK_MESSAGE(client.getId(), server.getId(), 
                               int(decodeMessage(message, "messageId"))))
    elif type == messageType["planet"]:
        newMessage = "planet of " + str(client.getId()) + ": " + "\""
        newMessage += client.getPlanetName() + "\""
        print(newMessage)    
    elif type == messageType["planetlist"]:
        planetList = decodeMessage(message, "buffer")
        print(planetList)
    else:
        print('error: type is', type)
    
def encodeMessage(client, message):
    messageTokens = message.split(' ')
    serverId = server.getId()
    messageId = server.getIncIdMessage()
    
    if messageTokens[0] == 'hi':
        client.messageIsHi()
        if len(messageTokens) == 2:
            return HI_MESSAGE(int(messageTokens[1]), serverId, messageId)
        else:
            return HI_MESSAGE(client.getId(), serverId, messageId)
    if messageTokens[0] == 'origin':
        planetName = messageTokens[2]
        client.setPlanetName(planetName)
        message = ORIGIN_MESSAGE(client.getId(), serverId, messageId, 
                                 messageTokens[1],planetName)
        return message
    
    if messageTokens[0] == 'kill':
        client.killClient()
        print("enviando kill")
        return KILL_MESSAGE(client.getId(), serverId, messageId)
    
    if messageTokens[0] == 'msg':
        newMessage = messageTokens[3]
        
        for i in range(4, len(messageTokens)):
            newMessage += ' ' + messageTokens[i]
            
        return MSG_MESSAGE(client.getId(), messageTokens[1], messageId, 
                           messageTokens[2], newMessage)
        
    if messageTokens[0] == 'creq':
        destin = messageTokens[1]
        return CREQ_MESSAGE(client.getId(),destin, messageId)

    if messageTokens[0] == 'planet':
        destin = messageTokens[1]
        return PLANET_MESSAGE(client.getId(), destin, messageId)
    
    if messageTokens[0] == 'planetlist':
        return PLANETLIST_MESSAGE(client.getId(), server.getId(), messageId)

# Todo: Os ids das mensagens não correspondem aos exemplos princiaplmente no quesito de hi e origin