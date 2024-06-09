/*

PROJET PROGRAMMATION RESEAU - STI - INSA CVL 2023/2024

Communication entre deux processus Python (par l'intermédiaire de processus C pour chacuns).
	-> PROTOCOLE TCP.

Fonctionnement :
	1 main pour le démarrage et l'arret.
	2 threads : un nouveau thread pour le PyToPlayer, le PlayerToPy reste dans le même thread que le main.
	Lorsque le thread PyToPlayer se ferme, le programme se termine automatiquement en repassant dans le main.
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
#define DEFAULT_PY_PORT 7000 //Destination port for the Py program
#define C_PORT 9000 //Destination port for the others C program
#define BUFLEN 1024 //Buffer length

#define NO_NOTIFS 1 //0 ou 1 pour autoriser ou non les notifications

typedef struct { //struct for all datas...
	struct sockaddr_in py_sockaddr; //socket to communicate with Py
	int py_sockfd;
	struct sockaddr_in serv_sockaddr; //socket for listenning to new C players
	int serv_sockfd;
	struct sockaddr_in player_sockaddr; //socket for communication with C players
	int player_sockfd;
	int nbPlayers; //number of players connected
	pthread_t thread_PlayerToPy; //thread for the PlayerToPy function
	char player_ip[20]; //IP of the player the client connects to
} data_struct;

void stop(char *s)
{
	perror(s);
	exit(EXIT_FAILURE);
}

void notification (data_struct data, char * msg)
/*
	Envoyer une notification au programme Python
*/
{
	if(NO_NOTIFS)
		return;
	else if (send(data.py_sockfd, msg, strlen(msg) , 0)==-1)
	{
		stop("send()");
	}
	return;
}

void PyToPlayer(data_struct data)
/*
	Fonction qui recoit les messages du Python et les transmet aux autres joueurs.
*/
{
	printf("PyToPlayer Loop Start\n");
	char msg[BUFLEN+1];
	while (1)
	{
		sleep(0.01);
		bzero(&msg,BUFLEN+1);
		//RECIEVE THE MESSAGE FROM PY
		if( recv(data.py_sockfd, msg, BUFLEN, 0) < 0 )
		{
			stop("recv failed. Error");
		}
		printf("$$ Recv From Py : %s\n", msg);
		// LECTURE DES INSTRUCTIONS SPECIFIQUES :
		if (strncmp(msg,"exit",4)==0)
		{
			//kill the program if we recieve "exit".
			notification(data, "## EXIT ##\n");
			printf("EXIT\n");
			return;
		}
		else if (strncmp(msg,"BecomeServer", 12)==0)
		{
			//become a TCP server and wait for other players to connect.
			notification(data, "## BECOME SERVER ##\n");
			printf("BECOME SERVER\n : %s\n", msg);
			BecomeServer(&data);
		}
		else if (strncmp(msg,"ConnectTo",9)==0)
		{
			notification(data, "## CONNECT TO ##\n");
			printf("CONNECT TO\n");
			//lecture de l'adresse IP du serveur, passée dans le message du python.
			int i=0;
			bzero(data.player_ip, 20);
			while(i<20 && msg[i+9]!='!')
				i++;
			strncpy(data.player_ip, msg+9, i);
			printf("IP to connect : %s\n", data.player_ip);
			notification(data, data.player_ip );
			//connect to the TCP server with the given IP address.
			ConnectToServer(&data);
		}
		// SEND THE MESSAGE FROM PY TO THE OTHER PLAYERS
		else if (send(data.player_sockfd, msg, strlen(msg) , 0)==-1)
		{
			stop("send()");
		}
		printf("$$ Sent to other player in C : %s\n", msg);
	}
}


void * PlayerToPy(data_struct * p_data)
/*
	Fonction qui envoie vers le python les message envoyés par les autres joueurs.
*/
{
	printf("PlayerToPy Loop Start\n");
	char msg[BUFLEN+1];
	while (1)
	{
		while (p_data->nbPlayers == 1)
		{
			bzero(&msg,BUFLEN+1);
			sleep(0.01);
			//RECIEVE FROM C
			if( recv(p_data->player_sockfd, msg, BUFLEN, 0) < 0 ){
				stop("recv failed. Error");
			}
			printf("$$ Recv From C : %s\n", msg);
			//SEND TO PY
			if (send(p_data->py_sockfd, msg, strlen(msg) , 0)==-1)
			{
				stop("send()");
			}
			printf("$$ Recv From C : %s\n", msg);
		}
		sleep(1); //need to keep the thread alive even if no C client is connected, else the killing instruction would fail.
	}
}

void ConnectToServer(data_struct * p_data)
{
	//Create the socket and connect to a server.
	printf("CONNECT TO SERVER\n");
	if ( (p_data->player_sockfd=socket(AF_INET, SOCK_STREAM , 0)) == -1)
	{
		stop("socket");
	}
	p_data->player_sockaddr.sin_addr.s_addr = inet_addr(p_data->player_ip);
	p_data->player_sockaddr.sin_family = AF_INET;
	p_data->player_sockaddr.sin_port = htons(C_PORT);
	//Connect to remote server
	if (connect(p_data->player_sockfd , (struct sockaddr *)&p_data->player_sockaddr , sizeof(p_data->player_sockaddr)) < 0)
	{
		stop("connect failed. Error");
	}
	p_data->nbPlayers++;
	printf("connected to : %s\n", p_data->player_ip);
	reload_thread(p_data); //RESTART THE THREAD PlayerToPy WITH THE UPDATED STRUCT.
	notification(*p_data, "## CONNECTED TO THE SERVER ##\n");
	printf("END OF ConnectToServer (success)\n");
}

void BecomeServer(data_struct * p_data)
/*
	Devenir un serveur TCP et attendre la connection des autres joueurs.
*/
{
	printf("BECOME SERVER\n");
	int clilen;
	char message[BUFLEN+1];

	if ( (p_data->serv_sockfd=socket(AF_INET, SOCK_STREAM , 0)) == -1)
	{
		stop("socket");
	}
	char myIP[20];
	bzero(myIP,20);
	getMyIp(myIP);
	if (strcmp(myIP, "error")==0) //error in getMyIp()
		strcpy(myIP,LOCAL);

	memset((char *) &(p_data->serv_sockaddr), 0, sizeof(p_data->serv_sockaddr));
	p_data->serv_sockaddr.sin_addr.s_addr = inet_addr(myIP);
	p_data->serv_sockaddr.sin_family = AF_INET;
	p_data->serv_sockaddr.sin_port = htons(C_PORT);
	
	// Binding newly created socket to given IP and verification 
	if ((bind(p_data->serv_sockfd, (struct sockaddr *)&(p_data->serv_sockaddr), sizeof(p_data->serv_sockaddr))) != 0)
	{
		stop("bind failed. Error");
	}

	// Now server is ready to listen	
	if (listen(p_data->serv_sockfd,5) != 0)
        {
                stop("listen failed. Error");
        }
	notification(*p_data, "## SERVER OPPENED ##\n");
	printf("Server Openned, waiting for other players to connect\n");
	// ACCEPT A CONNECTION
	memset(&(p_data->player_sockaddr), 0, sizeof(p_data->player_sockaddr));
	clilen = sizeof(p_data->player_sockaddr);
	if ((p_data->player_sockfd = accept(p_data->serv_sockfd, (struct sockaddr *) &(p_data->player_sockaddr), (socklen_t *)&clilen)) < 0){
		stop("accept failed. Error");
	}
	p_data->nbPlayers++;
	printf("Other player connected\n");
	reload_thread(p_data); //RESTART THE THREAD PlayerToPy WITH THE UPDATED STRUCT.
	notification(*p_data,"## OTHER PLAYER CONNECTED ##\n");
}


void reload_thread(data_struct * p_data)
{
	//RESTART THE THREAD PlayerToPy WITH THE UPDATED STRUCT.
	printf("RELOAD THREAD PlayerToPy\n");
	//close the thread SendToPy
	if (pthread_cancel(p_data->thread_PlayerToPy) != 0)
		stop("pthread_cancel error");
	printf("thread cancelled\n");
	//start the thread SendToPy
   	if (pthread_create(&p_data->thread_PlayerToPy,NULL,&PlayerToPy,p_data) != 0)
    	stop("pthread_create Sender");
	printf("thread started\n");
}

void getMyIp(char * buffer)
{
	const char* google_dns_server = "8.8.8.8";
    int dns_port = 53;
	
	struct sockaddr_in serv;
    
    int sock = socket ( AF_INET, SOCK_DGRAM, 0);
    
    //Socket could not be created
    if(sock < 0)
    {
		perror("Socket error");
	}
    
	memset( &serv, 0, sizeof(serv) );
    serv.sin_family = AF_INET;
    serv.sin_addr.s_addr = inet_addr( google_dns_server );
    serv.sin_port = htons( dns_port );

    int err = connect( sock , (const struct sockaddr*) &serv , sizeof(serv) );
    
    struct sockaddr_in name;
    socklen_t namelen = sizeof(name);
    err = getsockname(sock, (struct sockaddr*) &name, &namelen);

    const char* p = inet_ntop(AF_INET, &name.sin_addr, buffer, 100);
    	
	if(p != NULL)
	{
		printf("Local ip is : %s \n" , buffer);
	}
	else
	{
		//Some error
		printf ("Error number : %d . Error message : %s \n" , errno , strerror(errno));
		bzero(buffer, 20);
		strcpy(buffer, "error");
	}
    close(sock);
}

int main(int argc, char** argv)
{
	int py_port;

	if (argc>1)
		py_port = atoi(argv[1]);
	else
		py_port=DEFAULT_PY_PORT;

	printf("\n## LOGS ##\n\n\n");
	data_struct data;
	data.nbPlayers=0;

	printf("PY_PORT : %d\n", py_port);
	printf("C_PORT : %d\n", C_PORT);

	//create the socket to communicate with the python program
	if ( (data.py_sockfd=socket(AF_INET, SOCK_STREAM , 0)) == -1)
	{
		stop("socket");
	}
	data.py_sockaddr.sin_addr.s_addr = inet_addr(LOCAL);
	data.py_sockaddr.sin_family = AF_INET;
	data.py_sockaddr.sin_port = htons(py_port);
	
	//Connect to local Py program
	if (connect(data.py_sockfd , (struct sockaddr *)&data.py_sockaddr , sizeof(data.py_sockaddr)) < 0)
	{
		stop("connect failed. Error");
		return 1;
	}
	printf("# CONNECTED TO PY LOCAL GAME #\n");

	//lancer le thread SendToPy
   	if (pthread_create(&data.thread_PlayerToPy,NULL,&PlayerToPy,&data) != 0)
    	stop("pthread_create Sender");
	printf("Thread PlayerToPy started, in main()\n");
	
	//écouter les messages venant du python
	PyToPlayer(data); //cette fonction contient une boucle while et s'arrète lorsqu'on recoit "exit"

	/*
	* SI ON ATTEINT CETTE LIGNE, C'EST QU'ON A RECU "exit".
	*/

	printf("Exiting...\n");
	//fermer le thread SendToPy
	if (pthread_cancel(data.thread_PlayerToPy) != 0)
		stop("pthread_cancel thread_PlayerToPy"); 
	//fermer les sockets
	close(data.py_sockfd);
	close(data.serv_sockfd);
	close(data.player_sockfd);

	printf("Sockets closed\n\n");
	printf("Exit succesfull\n");
	sleep(1);

	return EXIT_SUCCESS;
}
