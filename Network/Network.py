from threading import *
import socket
import time
import errno
import subprocess
import struct
from Tiles.Bob.bob import Bob

#colors and style
BLACK   = "\033[30m"
RED     = "\033[31m"
GREEN   = "\033[32m"
YELLOW  = "\033[33m"
PURPLE = "\033[95m"
NOCOLOR = "\033[0m"
BOLD = '\033[1m'

#parameters
LOCAL = '127.0.0.1'
BUFSIZE = 1024

class Network:
    def __init__(self, port):
        #créer la socket qui écoute le programme C local.
        self.mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.mysocket.bind((LOCAL, port))
        self.mysocket.listen(1)
        print("\n")
        print(BOLD, RED, "PROJET PROGRAMMATION RESEAU - STI - INSA CVL 2023/2024", NOCOLOR)
        print("\n")
        print(BOLD, RED, "Serveur Allumé, sur le port", port, NOCOLOR)
        #lancer le processus C sur le port xxxx.
        cmd='./Network/client '+str(port)+' > Network/logs/log'+str(port)+'.txt & '
        subprocess.run([cmd], shell=True)
        #accepter la connection du processus C
        self.connection, retaddr = self.mysocket.accept()
        self.connection.setblocking(False)
        print(BOLD, RED,"Connecté au programme C local", NOCOLOR)
        print("\n")
        #Création d'un packet pour l'envoi, avec sérialisation des données qu'il contient
        self.data = None
    
    def encode_data(self, data):
        if isinstance(data, str): #message is a str
            self.data= "S"
            self.data += data
            print(self.data)
        elif isinstance(data, Bob): #message is a Bob
            self.data = "B"
            self.data += f"{data.id},{data.age},{data.isHunting},{data.alreadyInteracted},{data.energy},{data.energyMax},{data.mass},{data.velocity},{data.speed},{data.vision}"
        else:
            print("self.data est toujours vide")
            exit()

    def decode_data(self):
        if self.data[0]=="S": #message is a str
            return self.data[1:]
        if self.data[0]=="B":
            bob_data = self.data[1:].split(',')
            new_bob = Bob()  # Crée une nouvelle instance de Bob
            new_bob.id = (bob_data[0])
            new_bob.age = (bob_data[1])
            new_bob.isHunting = bob_data[2]
            new_bob.alreadyInteracted = bob_data[3]
            new_bob.energy = (bob_data[4])
            new_bob.energyMax = (bob_data[5])
            new_bob.mass = (bob_data[6])
            new_bob.velocity = (bob_data[7])
            new_bob.speed = (bob_data[8])
            new_bob.vision = (bob_data[9])
            return new_bob


    def receive(self):
        try :
            self.data = self.connection.recv(BUFSIZE).decode()
            if len(self.data)>0:
                print(GREEN, "->> Recv\n", NOCOLOR)
                return self.decode_data()
        except socket.error as e:
            if e.errno == errno.EWOULDBLOCK : #in this case, this is a timeout error because we didn't received any message, so everything is fine !
                #print("No Data Received")
                time.sleep(0.1)
                return None
            else : #Other error -> problem ! (I've never had any issue, yet)
                print(BOLD, RED, "\n ERROR in the receive fct", NOCOLOR)
                self.exit()
                
    def send(self, data):
        self.encode_data(data)
        self.connection.send(self.data.encode())
        print (PURPLE, "<<- Send\n", NOCOLOR)

    def exit(self):
        """
        Function to exit safely.
        """
        time.sleep(0.1)
        print("\n")
        self.connection.send("exit".encode()) #terminer le programme C
        time.sleep(0.1)
        #Close the sockets
        self.connection.close()
        self.mysocket.close()
        print("\n")
        print(RED, BOLD, "Fermeture des sockets OK \n", NOCOLOR)

    def openServerOnC(self):
        """
        Function to turn the C client into a server waiting for the other C player to connect.
        BLOCKING FUNCTION !
        """
        connected=False
        self.connection.send("BecomeServer".encode()) #Listen as a server
        while not connected:
            #Recevoir les messages en attendant la confirmation.
            msg=""
            try :
                msg = self.connection.recv(BUFSIZE).decode()
            except socket.error as e:
                if e.errno == errno.EWOULDBLOCK : #in this case, this is a timeout error because we didn't received any message, so everything is fine !
                    #print("No Data Received")
                    time.sleep(0.1)
                else : #Other error -> problem ! (I've never had any issue, yet)
                    print(BOLD, RED, "\n ERROR in the receive fct", NOCOLOR)
                    self.exit()
            if msg=="CONNECTED":
                connected=True
        print(GREEN, "C CONNECTED TO OTHER PLAYER\n", NOCOLOR)

    def connectToServerOnC(self, IP):
        """
        Function to turn the C client into a client connecting to the Other player waiting for us to join.
        BLOCKING FUNCTION !
        """
        connected=False
        msg="ConnectTo"+IP+"!" #IP is type str
        self.connection.send(msg.encode()) #CONNECT AS A CLIENT
        while not connected:
            #Recevoir les messages en attendant la confirmation.
            msg=""
            try :
                msg = self.connection.recv(BUFSIZE).decode()
            except socket.error as e:
                if e.errno == errno.EWOULDBLOCK : #in this case, this is a timeout error because we didn't received any message, so everything is fine !
                    #print("No Data Received")
                    time.sleep(0.1)
                else : #Other error -> problem ! (I've never had any issue, yet)
                    print(BOLD, RED, "\n ERROR in the receive fct", NOCOLOR)
                    self.exit()
            if msg=="CONNECTED":
                connected=True
        print(GREEN, "C CONNECTED TO OTHER PLAYER\n", NOCOLOR)
