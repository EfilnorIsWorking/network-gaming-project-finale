/*

PROJET PROGRAMMATION RESEAU - STI - INSA CVL 2023/2024

Titouan GODARD 

Communication entre C et Python en local.
	-> PROTOCOLE TCP.

DANS LE PROGRAMME C : La partie Py To C tourne dans le programme principal, et C To Py tourne dans un thread dédié.
DANS LE PROGRAMME Py : Execution linéaire.
Le python peut terminer le programme C en lui envoyant "exit".

Utilisation : 
	- compiler tcpclient.c :	gcc tcpclient.c -o tcpclient 
	- executer le python :		/bin/python3 ./tcpserver.py

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
		sleep(0.01);
		bzero(&msgIn,BUFLEN+1);
        	if( recv(sockets.py_sockfd, msgIn, BUFLEN, 0) < 0 ) 
			{
            	stop("recv failed. Error");
        	}
        	//printf("Recv : %s\n", msgIn);
			if (send(sockets.py_sockfd, msgIn, strlen(msgIn) , 0)==-1)
			{
				stop("send()");
			}
			// faire suivre le message reçu du python vers les autres joueurs en C.
			if (strcmp(msgIn,"exit")==0)
			{
				//kill the program if we recieve "exit".
				//printf("Quitter");
				return;
			}
	}
}


void * sendToPy(sockets_struct * pointeur_sockets)
/*
Fonction qui envoie vers le python les message saisis dans le terminal.
*/
{
	int py_sockfd = pointeur_sockets->py_sockfd;
	char msgOut[BUFLEN+1];
	while (1)
	{
		sleep(0.01);
		scanf("%s", msgOut);
			//send the message
			msgOut[BUFLEN]='\0';
			//printf("Send %s\n",msgOut);
			if (send(py_sockfd, msgOut, strlen(msgOut) , 0)==-1)
			{
				stop("send()");
			}
			//printf("Send : %s\n", msgOut);
	}
}


int main(int argc, char** argv)
{
	int port;

	if (argc>1)
		port = atoi(argv[1]);
	else
		port=DEFAULT_PORT;
		
	sockets_struct sockets;

	if ( (sockets.py_sockfd=socket(AF_INET, SOCK_STREAM , 0)) == -1)
	{
		stop("socket");
	}

	sockets.py_sockaddr.sin_addr.s_addr = inet_addr(LOCAL);
	sockets.py_sockaddr.sin_family = AF_INET;
	sockets.py_sockaddr.sin_port = htons(port);
	
	//Connect to local Py program
	if (connect(sockets.py_sockfd , (struct sockaddr *)&sockets.py_sockaddr , sizeof(sockets.py_sockaddr)) < 0)
	{
		stop("connect failed. Error");
		return 1;
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
