"""

PROJET PROGRAMMATION RESEAU - STI - INSA CVL 2023/2024

Titouan GODARD 

Communication entre C et Python en local.
	-> PROTOCOLE UDP.

DANS LE PROGRAMME C : La partie Py To C tourne dans le programme principal, et C To Py tourne dans un thread dédié.
DANS LE PROGRAMME Py : Execution linéaire.
Le python peut terminer le programme C en lui envoyant "exit".

Utilisation : 
    - pour changer le port :    modifier dans Py la variable globale et le paramètre de la commande os.system() L53.
	- compiler udpclient.c :	gcc udpclient.c -o udpclient 
	- executer le python :		/bin/python3 ./udpserver.py

"""


from threading import *
import socket
import time
import os
import errno
import subprocess

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
PORT = 9000
BUFSIZE = 1024

class Communication:
    def __init__(self):
        #créer la socket qui écoute le programme C local.
        self.mysocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        self.mysocket.bind((LOCAL, PORT))
        print("\n")
        print(BOLD, RED, "PROJET PROGRAMMATION RESEAU - STI - INSA CVL 2023/2024", NOCOLOR)
        print("\n")
        print(BOLD, RED, "Serveur UDP Allumé, sur le port", PORT, NOCOLOR)
        #lancer le processus C sur le port xxxx.
        os.system(r'./udpclient 9000 &')
        #accepter la connection du processus C
        bytesAddressPair = self.mysocket.recvfrom(BUFSIZE)   # recvfrom renvoie un tuple (message, addr)
        self.connection = bytesAddressPair[1] #connection to the C socket
        print(BOLD, RED,"Connecté au programme C local", NOCOLOR)
        print("\n")
        

    def recieve(self):    
        msgIn = self.mysocket.recvfrom(BUFSIZE)[0]
        if len(msgIn)>0:
            print(GREEN, "->> Recv : ", msgIn.decode(), NOCOLOR)
            if msgIn.decode() == 'exit':
                print(BOLD, RED, "### Exit ###", NOCOLOR)
                self.exit()
            ########################################
            # mettre a jour les données du jeu ici #
            ########################################
                
    def send(self, msgOut):
        self.mysocket.sendto(msgOut.encode(), self.connection)
        print (PURPLE, "Send : ", msgOut, NOCOLOR)
        
    def exit(self):
        """
        Function to exit safely.
        """
        time.sleep(0.1)
        print("\n")
        ConnectionToC.send("exit") #terminer le programme C
        time.sleep(0.1)
        #Close the socket
        self.mysocket.close()
        print("\n")
        print(RED, BOLD, "Fermeture des sockets OK \n", NOCOLOR)

    
ConnectionToC = Communication()

#cette partie simule les ticks.
startTime=time.time()
lastSendTime=time.time()
while time.time()-startTime < 60 : #run for x seconds
    if time.time()-lastSendTime > 0.5 : #send Bip every 0.5 seconds
        ConnectionToC.send("Bip")
        lastSendTime=time.time()
    else : ConnectionToC.recieve() #Listen

ConnectionToC.exit()