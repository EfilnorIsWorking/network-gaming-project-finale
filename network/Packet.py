import pickle
import sys
from socket import gethostname, gethostbyname

class Packet:
    def __init__(self,type,receiver):
        self.type = type #Type de packet
        self.content = [] #Contenue totale de la data d'un packet
        self.sender = gethostbyname(gethostname())
        self.receiver = receiver
        self.serialized_data = []
        self.isFull = False
    
    @property
    def getcontent(self):
        return self.data

    @property
    def gettype(self):
        return self.type
    
    def data_add(self,data):
        if self.isFull==False or sys.getsizeof(str(self.sender) + str(self.receiver)+ str(self.type) + [str(element) for element in self.content]+ str(data)) < 1024:
            self.content.append(data) 
            return True
        else:
            self.isFull = True
            return "Packet is full"
    
    def serialize(self):
        self.serialized_data = pickle.dumps([self.sender,self.receiver,self.type,self.content])

    def deserialize(self,data):
        self.type = data[0]
        self.content = data[2][:-1]
        return (self.type,self.content)
