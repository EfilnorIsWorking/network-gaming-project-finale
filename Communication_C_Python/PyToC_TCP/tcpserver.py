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
        self.mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.mysocket.bind((LOCAL, PORT))
        self.mysocket.listen(1)
        print("\n")
        print(BOLD, RED, "PROJET PROGRAMMATION RESEAU - STI - INSA CVL 2023/2024", NOCOLOR)
        print("\n")
        print(BOLD, RED, "Serveur Allumé, sur le port", PORT, NOCOLOR)
        #lancer le processus C sur le port xxxx.
        os.system(r'./tcpclient 9000 &')
        #accepter la connection du processus C
        self.connection, retaddr = self.mysocket.accept()
        self.connection.setblocking(False)
        print(BOLD, RED,"Connecté au programme C local", NOCOLOR)
        print("\n")

    def receive(self):    
        try :
            msgIn = self.connection.recv(BUFSIZE)
            print(GREEN, "->> Recv : ", msgIn.decode(), NOCOLOR)
            if msgIn.decode() == 'exit':
                print(BOLD, RED, "### Exit ###", NOCOLOR)
                self.exit()
            ########################################
            # mettre a jour les données du jeu ici #
            ########################################
        except socket.error as e:
            if e.errno == errno.EWOULDBLOCK : #in this case, this is a timeout error because we didn't received any message, so everything is fine !
                #print("No Data Received")
                time.sleep(0.1)
                return
            else : #Other error -> problem ! (I've never had any issue, yet)
                print(BOLD, RED, "\n ERROR in the receive fct", NOCOLOR)
                self.exit()
                
    def send(self, msgOut):
        self.connection.send(msgOut.encode())
        print (PURPLE, "Send : ", msgOut, NOCOLOR)
        
    def exit(self):
        """
        Function to exit safely.
        """
        time.sleep(0.1)
        print("\n")
        ConnectionToC.send("exit") #terminer le programme C
        time.sleep(0.1)
        #Close the sockets
        self.connection.close()
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
    else : ConnectionToC.receive() #Listen

ConnectionToC.exit()
