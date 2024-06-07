/*

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

*/


#include <string.h>
#include <arpa/inet.h>
#include <errno.h>
#include <netinet/in.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <strings.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>
#include <pthread.h>

#define LOCAL "127.0.0.1" //localhost
#define DEFAULT_PORT 9000 //Destination port
#define BUFLEN 1024 //Buffer length

typedef struct {
	struct sockaddr_in py_sockaddr;
	int py_sockfd;
	socklen_t py_addr_size;
	struct sockaddr_in player_sockaddr;
	int player_sockfd;
} sockets_struct;

void stop(char *s)
{
	perror(s);
	exit(EXIT_FAILURE);
}

void recieveFromPy(sockets_struct sockets)
/*
Fonction qui recoit les messages du Python.
*/
{
	char msgIn[BUFLEN+1];
	while (1)
	{
		bzero(&msgIn,BUFLEN+1);
        	if(recvfrom(sockets.py_sockfd, msgIn, BUFLEN, 0, NULL, &sockets.py_addr_size) < 0) 
			{
            	stop("recvfrom failed. Error");
        	}
        	//printf("Recv : %s\n", msgIn);
			if (sendto(sockets.py_sockfd, msgIn, strlen(msgIn) , 0, (struct sockaddr *) &sockets.py_sockaddr, sockets.py_addr_size) == -1)
			{
				stop("sendto() failed");
			}
			// faire suivre le message reçu du python vers les autres joueurs en C.
			if (strcmp(msgIn,"exit") == 0)
			{
				//kill the program if we recieve "exit".
				//printf("Quitter");
				return;
			}
	}
}


void * sendToPy(sockets_struct * p_sockets)
/*
Fonction qui envoie vers le python les message saisis dans le terminal.
*/
{
	char msgOut[BUFLEN+1];
	while (1)
	{
		//scanning the standard input
		scanf("%s", msgOut);
		//send the message
		msgOut[BUFLEN]='\0';
		//printf("Send %s\n",msgOut);
		if (sendto(p_sockets->py_sockfd, msgOut, strlen(msgOut) , 0, (struct sockaddr *) &p_sockets->py_sockaddr, p_sockets->py_addr_size) == -1)
		{
			stop("sendto() failed");
		}
		//printf("Send : %s\n", msgOut);
	}
}


int main(int argc, char** argv)
{
	//Select the right port
	int port;
	if (argc>1) //port given in the args
		port = atoi(argv[1]);
	else //default port if no arg given
		port=DEFAULT_PORT;
		
	sockets_struct sockets;

	if ( (sockets.py_sockfd=socket(AF_INET, SOCK_DGRAM, 0)) == -1)
	{
		stop("socket creation failed");
	}

	memset((char*) &sockets.py_sockaddr, 0, sizeof(sockets.py_sockaddr));
	sockets.py_sockaddr.sin_family = AF_INET;
	sockets.py_sockaddr.sin_port = htons(port);
	sockets.py_sockaddr.sin_addr.s_addr = inet_addr(LOCAL);
	sockets.py_addr_size=sizeof(sockets.py_sockaddr);

	//Connect to local Py program (sending a simple message to share my address)
	if (sendto(sockets.py_sockfd, "Conncetion", strlen("Connection") , 0, (struct sockaddr *) &sockets.py_sockaddr, sockets.py_addr_size) == -1)
	{
		stop("sendto() failed");
	}
	//printf("Connected\n");
	


	//lancer le thread SendToPy
	pthread_t thread_SendToPy;
   	if (pthread_create(&thread_SendToPy,NULL,&sendToPy,&sockets) != 0)
    	stop("pthread_create Sender");
	
	//écouter les messages venant du python
	recieveFromPy(sockets); //cette fonction contient une boucle while et s'arrète lorsqu'on recoit "exit"
	
	/*
	*		SI ON ATTEINT CETTE LIGNE, C'EST QU'ON A RECU "exit".
	*/

	//fermer le thread SendToPy
	if (pthread_cancel(thread_SendToPy) != 0)
		stop("pthread_cancel thread_SendToPy"); 
	//fermer les sockets
	close(sockets.py_sockfd);
	close(sockets.player_sockfd);
	
	//printf("Exit succesfull...\n");
	sleep(1);

	return EXIT_SUCCESS;
}
