import socket
import sys

    
def lookupList(elems, id):
    for elem in elems:
        if elem.getId() == id:
            return elem
    print("Couldn't find exhibitor id")
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
    #print('strMessage:', strMessage)
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
            
def getDestinFromMessage(message):
    return int(decodeMessage(message, "destin"))

def getOriginFromMessage(message):
    return int(decodeMessage(message, "origin"))

def getTypeFromMessage(message):
    return int(decodeMessage(message, "type"))

def getBufferSizeFromMessage(message):
    return int(decodeMessage(message, "bufferSize"))

def getBufferFromMessage(message):
    #print("tentado recuperar msg do buffer da msg")
    return decodeMessage(message, "buffer")

def getMessageIdFromMessage(message):
    return int(decodeMessage(message, "messageId"))

#TODO: indicar erro para o caso do id ser maior que o range

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
        self.clients = set()
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
        
    def printExhibitorIds(self):
        listIds = []
        for exhibitor in self.exhibitors:
            listIds.append(exhibitor.getId())
        print("Exhibitors live: ", listIds)
   
    def printBroadcasterIds(self):
        listIds = []
        for broadcaster in self.broadcasters:
            listIds.append(broadcaster.getId())
        print("Broadcastes live:", listIds)
    
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
        #print("Clients live:", listIds)
        return listIds    
    
    def getPlanetOfId(self, id):
        for client in self.getClients():
            if client.getId() == id:
                return client.getPlanetName()
    
        return "error"
   
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
        self.exhibitorId = -1
        self.role = "broadcaster"
        
    def setExhibitor(self, exhibitor):
        self.exhibitorId = exhibitor
        
    def getExhibitorId(self):
        return self.exhibitorId
    
    def printClient(self):
        print(' -> Role:', self.role)
        print('    planet:', self.planetName)
        print('    id:', self.id)
        print('    exhibitorId:', self.exhibitorId)
    
class Exhibitor(Client):
    def __init__(self, id, socket):
        Client.__init__(self, id, socket)
        self.broadcasterId = 0
        self.role = "exhibitor"
        
    def setBroadcaster(self, broadcaster):
        self.broadcasterId = broadcaster
        
    def getBroadcasterId(self):
        return self.broadcasterId
    
    def printClient(self):
        print(' -> Role:', self.role)
        print('    planet:', self.planetName)
        print('    id:', self.id)
        print('    broadcasterId:', self.broadcasterId)

def eval(client, message):
    if len(message) == 0:
        return 1
    
    type = getTypeFromMessage(message)
    if type == messageType["ok"]:
        if client.lastMessageWasHi():
            client.messageIsNotHi()
            client.setId(getDestinFromMessage(message))
            print("< ok " + str(getDestinFromMessage(message)))
        elif not client.isLive():
            print("< ok kill")
            client.killClient()
            client.close()
            return -1
        else:
            print("< ok")
            return 0
    elif type == messageType["kill"]:
        print("< kill")
        client.killClient()
        client.close()
        return -1 
    elif type == messageType["error"]:
        print("< error")
    elif type == messageType["msg"]:
        origin = getOriginFromMessage(message)
        messageRecieved = getBufferFromMessage(message)
        print('< msg from ' + str(origin) + ': ' + '\"' + str(messageRecieved) +  '\"')   
    elif type == messageType["clist"]:
        clist = getBufferFromMessage(message)
        print(clist)
    elif type == messageType["planet"]:
        newMessage = "planet of " + str(client.getId()) + ": " + "\""
        newMessage += client.getPlanetName() + "\""
        print(newMessage)    
    elif type == messageType["planetlist"]:
        planetList = getBufferFromMessage(message)
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
        destin = messageTokens[1]
        return PLANETLIST_MESSAGE(client.getId(), destin, messageId)

# Todo: Erro ao fechar a conexão quando não há um exibidor associado
# Todo: mensagens que devem ser enviadas ao exibidor de um emissor dado como destino não são repassadas
# Todo: Os ids das mensagens não correspondem aos exemplos princiaplmente no quesito de hi e origin
# Todo: passar ip e porta via argumentos