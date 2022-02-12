import socket
import sys

# Registro de clientes Broadcasters
broadcasters = []
logMessagesBroadcasters = []

# Registro de clientes Exhibitors
exhibitors = []
logMessagesExhibitors = []

logMessagesServidor = []

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
    print('strMessage:', strMessage)
    listAttributes = strMessage.split("|")
    if  attribute == "type":
        return listAttributes[1]
    elif attribute == "origin":
        return listAttributes[2]
    elif attribute == "destin":
        return listAttributes[3]
    elif attribute == "buffer":
        if len(listAttributes) > 6:
            return listAttributes[6].split(' ')[1]
        else:
            sys.exit("Trying to return Buffer from a message without it.")
            
def getDestinFromMessage(message):
    return int(decodeMessage(message, "destin"))

def getOriginFromMessage(message):
    return int(decodeMessage(message, "origin"))

def getTypeFromMessage(message):
    return int(decodeMessage(message, "type"))

def getPlanetNameFromOriginMessage(client, message):
    planetName = decodeMessage(message, "buffer")
    return planetName

#TODO: indicar erro para o caso do id ser maior que o range

def MESSAGE(tipo, orig, dest, idMessage):
    message = "| " + str(tipo) + " | " + str(orig) + " | "+ str(dest) + " | " + str(idMessage) + " |"
    return message.encode('UTF-8')
    
def EXT_MESSAGE(tipo, orig, dest, idMessage, bufferSize, buffer):
    oldMessage = MESSAGE(messageType["origin"], orig, dest, idMessage)
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

class Server: 
    def __init__(self):
        self.id = (pow(2, 16) - 1)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.idMessage = 0
        self.exhibitorCounter = rangeIdExhibitor[0] - 1
        self.broadcasterCounter = rangeIdBroadcaster[0] - 1
        self.clients = set()
        
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
    
        

class Client:
    def __init__(self, idClient, socketClient):
        self.id = idClient
        self.socket = socketClient
        #self.address = addressClient
        self.planetName = ""
        self.Hi = False
        self.Kill = False
        self.role = ""
        
    def addPlanetName(self, name):
        self.planetName = name
        
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
    
    def lastMessageWasKill(self):
        return self.Kill
    
    def messageIsKill(self):
        self.Kill = True
        
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
    type = getTypeFromMessage(message)
    if type == messageType["ok"]:
        if client.lastMessageWasHi():
            client.messageIsNotHi()
            client.setId(getDestinFromMessage(message))
            print("< ok " + str(getDestinFromMessage(message)))
        elif client.lastMessageWasKill():
            print("< ok kill")
            client.close()
            return -1
        else:
            print("< ok")
    elif type == messageType["kill"]:
        print("< kill")
        client.close()
        return -1        
    else:
        print('error: type is', type)

    #if type == messageType["hi"]:
    #    return evalHiClient(message)
    #elif type == messageType["origin"]:
    #    return evalOriginClient(message)
    
def encodeMessage(broadcaster, message):
    messageTokens = message.split(' ')
    serverId = server.getId()
    messageId = server.getIncIdMessage()
    
    if messageTokens[0] == 'hi':
        broadcaster.messageIsHi()
        if len(messageTokens) == 2:
            return HI_MESSAGE(int(messageTokens[1]), serverId, messageId)
        else:
            return HI_MESSAGE(broadcaster.getId(), serverId, messageId)
    if messageTokens[0] == 'origin':
        planetName = messageTokens[2]
        message = ORIGIN_MESSAGE(broadcaster.getId(), serverId, messageId, 
                                 messageTokens[1],planetName)
        return message
    
    if messageTokens[0] == 'kill':
        broadcaster.messageIsKill()
        print("enviando kill")
        return KILL_MESSAGE(broadcaster.getId(), serverId, messageId)
        
    
server = Server()