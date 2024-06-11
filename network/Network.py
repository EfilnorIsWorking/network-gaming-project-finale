from network.Packet import *

import pickle

from threading import *
import socket
import time
import os
import errno
import subprocess

from Tiles.Bob import bob
from Tiles.tiles import Tile

class Network:
    def __init__(self,LOCAL = '127.0.0.1',PORT = 9000,BUFSIZE = 1024):

        filename = "client"
        if not os.path.exists(filename):
            os.system("gcc -o Network/client Network/client.c")
        
        self.player_lists=[] #Liste de joueurs 
        self.id = None       #Id de notre client

        self.BUFSIZE = BUFSIZE
        self.LOCAL = LOCAL
        self.PORT = PORT

        self.buff_receive = [] #Buffer de réception

        self.BLACK   = "\033[30m" #Couleurs d'affichage
        self.RED     = "\033[31m"
        self.GREEN   = "\033[32m"
        self.YELLOW  = "\033[33m"
        self.PURPLE = "\033[95m"
        self.NOCOLOR = "\033[0m"
        self.BOLD = '\033[1m'

        #créer la socket qui écoute le programme C local.
        self.mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.mysocket.bind((LOCAL, PORT))
        self.mysocket.listen(1)
        print("\n")
        print(self.BOLD, self.RED, "PROJET PROGRAMMATION RESEAU - STI - INSA CVL 2023/2024", self.NOCOLOR)
        print("\n")
        print(self.BOLD, self.RED, "Serveur Allumé, sur le port", PORT, self.NOCOLOR)
        print(os.getcwd())
        #lancer le processus C sur le port xxxx.
        program_win = os.path.join(os.path.dirname(__file__), "tcpclient_win.exe")
        program_unix = os.path.join(os.path.dirname(__file__), "tcpclient_unix")

        # Define the arguments for the executable
        arguments = ["9000"]

        # Create the command as a list
        

        # Use subprocess.Popen to run the command
        if os.name == 'nt':
            command = [program_win] + arguments
            
        elif os.name == 'posix':
            command = [program_unix] + arguments
        else:
            print('This is not a Windows or Unix-like system.')
            exit()
        process = subprocess.Popen(command, shell=True)
        self.connection, retaddr = self.mysocket.accept()
        self.connection.setblocking(False)
        print(self.BOLD, self.RED,"Connecté au programme C local", self.NOCOLOR)
        print("\n")

    def receive(self):    
        try :
            msgIn = self.connection.recv(self.BUFSIZE)
            self.buff_receive.append(msgIn)
            print(self.GREEN, "->> Recv : ", msgIn, self.NOCOLOR)
            try:
                if msgIn.decode() == 'exit':
                    print(self.BOLD, self.RED, "### Exit ###", self.NOCOLOR)
                    self.exit()
            except:
                pass
            ########################################
            # mettre a jour les données du jeu ici #
            ########################################
        except socket.error as e:
            if e.errno == errno.EWOULDBLOCK : #in this case, this is a timeout error because we didn't received any message, so everything is fine !
                #print("No Data Received")
                time.sleep(0.1)
                return
            else : #Other error -> problem ! (I've never had any issue, yet)
                print(self.BOLD, self.RED, "\n ERROR in the receive fct", self.NOCOLOR)
                self.buff_receive.append("ERROR")
                self.exit()
    
    #On efface le buffer de réception
    def receive_clear(self):
        self.buff_receive = []

    def send(self, msgOut):
        if isinstance(msgOut,Packet):
            self.connection.send(msgOut.serialized_data)
        elif isinstance(msgOut,str):
            self.connection.send(msgOut.encode())
        else:
            try:
                self.connection.send(msgOut.encode())
            except:
                print("Unavailable data type")
        print (self.PURPLE, "Send : ", msgOut, self.NOCOLOR)

    def exit(self):
        """
        Function to exit safely.
        """
        time.sleep(0.1)
        print("\n")
        self.send("exit") #terminer le programme C
        time.sleep(0.1)
        #Close the sockets
        self.connection.close()
        self.mysocket.close()
        print("\n")
        print(self.RED, self.BOLD, "Fermeture des sockets OK \n", self.NOCOLOR)

    def add_player(self,players):
        try:
            for player in players:
                self.player_list.append(player)
        except:
            return False
        
    def declare_new_player(self):      
            packets = []
            packet = Packet("AddPlayer",self.id,"BROADCAST")
    
    def remove_player(self, players):
        try:
            for player in players:
                self.player_list.remove(player)
        except:
            return False
        
    def leaving(self):
        packet = Packet("RemovePlayer",self.id,"BROADCAST")
        packet.serialize()
        #envoyer le paquet
        return True
        
    def ask_to_access_network_property(self,things):
        '''
        Demande l'accès à la propriété d'un objet
        '''
        packets = []
        packet = Packet("AskNetworkProperty")
        while things:
            data = things.pop()
            while packet.isFull == False:
                packet.data_add(data)
                data = things.pop()
            packets.append(packet)
            packet = Packet("AskNetworkProperty")
        for i in packets:
            i.serialize()
            self.send(packet)

    def answer_network_property(self,thing):
        '''
        Répond à une demande d'accès à la propriété d'un objet
        '''
        if thing.isinstance(bob) or thing.isinstance(Tile):
            packet = Packet("AnswerNetworkProperty")
            packet.data_add(thing.network_property)
            packet.serialize()
            self.send(packet)
    
    def verify_owner_property(self,thing,player):
        if thing.isinstance(bob) or thing.isinstance(Tile):
            if thing.owner_property == player:
                return True
            else:
                return False
        else:
            return "This Object can't have a property_owner"
        
    def packet_sorting(self,packet): 
        '''
        Cette fonction trie les paquets en fonction de leur type. Et appelle les fonctions qui les traitent
        '''
        if packet.content != []:

            if(type == "AskNetworkProperty"):
                for  i in packet.content: 
                    self.answer_network_property(self,i)
            elif(type == "Leaving"): 
                for i in packet.content:
                        self.remove_player(self,i)
            #... 
            else: 
            #message d'erreur ou qqch comme ça
                pass
