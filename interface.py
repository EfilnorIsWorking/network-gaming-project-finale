"""

PROJET PROGRAMMATION RESEAU - STI - INSA CVL 2023/2024

Titouan GODARD

Communication entre C et Python en local.
	-> PROTOCOLE TCP.

DANS LE PROGRAMME C : La partie Py To C tourne dans le programme principal, et C To Py tourne dans un thread dédié.
DANS LE PROGRAMME Py : Execution linéaire.
Le python peut terminer le programme C en lui envoyant "exit".

Utilisation :
    - pour changer le port :    modifier dans Py la variable globale et le paramètre de la commande os.system() L53.
	- compiler tcpclient.c :	gcc tcpclient.c -o tcpclient
	- executer le python :		/bin/python3 ./tcpserver.py

"""


from threading import *
import socket
import time
import os
import errno
import subprocess
import pickle
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
PORT = 8000
BUFSIZE = 1024

class Network:
    def __init__(self):
        #créer la socket qui écoute le programme C local.
        self.mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.mysocket.bind((LOCAL, PORT))
        self.mysocket.listen(1)
        print("\n")
        print(BOLD, RED, "PROJET PROGRAMMATION RESEAU - STI - INSA CVL 2023/2024", NOCOLOR)
        print("\n")
        print(BOLD, RED, "Serveur Allumé, sur le port", PORT, NOCOLOR)
        #lancer le processus C sur le port xxxx.
        subprocess.run(['./client 8000 > log.txt & '], shell=True)
        #os.system(r'./client 7000 > log.txt & ')
        #accepter la connection du processus C
        self.connection, retaddr = self.mysocket.accept()
        self.connection.setblocking(False)
        print(BOLD, RED,"Connecté au programme C local", NOCOLOR)
        print("\n")
        #Création d'un packet pour l'envoi, avec sérialisation des données qu'il contient
        self.data = None
    
    def encode_data(self, data):
        if isinstance(data, str):
            self.data= "S"
            self.data += data
            print(self.data)
        elif isinstance(data, Bob):
            self.data = "B"
            self.data += f"{data.id},{data.age},{data.isHunting},{data.alreadyInteracted},{data.energy},{data.energyMax},{data.mass},{data.velocity},{data.speed},{data.vision}"
        else:
            print("self.data est toujours vide")
            exit()

    def decode_data(self):
        if self.data[0]=="S": #message is a str
            return self.data[1:]
        elif self.data[0]=="B":
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
            return new_bob[1:] #ou new_bob

    def recieve(self):    
        try :
            self.data = self.connection.recv(BUFSIZE).decode()
            print(GREEN, "->> Recv\n", NOCOLOR)
            return self.decode_data()
        except socket.error as e:
            if e.errno == errno.EWOULDBLOCK : #in this case, this is a timeout error because we didn't received any message, so everything is fine !
                #print("No Data Received")
                time.sleep(0.1)
                return None
            else : #Other error -> problem ! (I've never had any issue, yet)
                print(BOLD, RED, "\n ERROR in the recieve fct", NOCOLOR)
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


ConnectionToC = Network()

#cette partie simule les ticks.
startTime=time.time()
lastSendTime=time.time()

#CHOSE HERE !!!!!!!!!!!!!!
#####################################################################################
#ConnectionToC.send("BecomeServer") #CONNECT AS A SERVER #CONNECT AS A CLIENT
ConnectionToC.connection.send("ConnectTo192.168.232.128!".encode())
#####################################################################################
time.sleep(10)
ConnectionToC.send("HELLO")
        
time.sleep(5)

ConnectionToC.exit()
