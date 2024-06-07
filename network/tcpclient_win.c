#include <winsock2.h>
#include <ws2tcpip.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define LOCAL "127.0.0.1" //localhost
#define DEFAULT_PORT "9000" //Destination port
#define BUFLEN 1024 //Buffer length

typedef struct {
    struct sockaddr_in py_sockaddr;
    SOCKET py_sockfd;
    struct sockaddr_in player_sockaddr;
    SOCKET player_sockfd;
} sockets_struct;

void stop(const char *s)
{
    fprintf(stderr, "%s: %d\n", s, WSAGetLastError());
    exit(EXIT_FAILURE);
}

DWORD WINAPI sendToPy(LPVOID lpParam)
{
    sockets_struct* pointeur_sockets = (sockets_struct*)lpParam;
    SOCKET py_sockfd = pointeur_sockets->py_sockfd;
    char msgOut[BUFLEN+1];
    while (1)
    {
        Sleep(10);
        scanf("%s", msgOut);
        msgOut[BUFLEN]='\0';
        if (send(py_sockfd, msgOut, strlen(msgOut) , 0)==SOCKET_ERROR)
        {
            stop("send()");
        }
    }
    return 0;
}

void recieveFromPy(sockets_struct sockets)
{
    char msgIn[BUFLEN+1];
    while (1)
    {
        Sleep(10);
        memset(&msgIn, 0, sizeof(msgIn));
        if( recv(sockets.py_sockfd, msgIn, BUFLEN, 0) == SOCKET_ERROR ) 
        {
            stop("recv failed. Error");
        }
        if (send(sockets.py_sockfd, msgIn, strlen(msgIn) , 0)==SOCKET_ERROR)
        {
            stop("send()");
        }
        if (strcmp(msgIn,"exit")==0)
        {
            return;
        }
    }
}

int main(int argc, char** argv)
{
    WSADATA wsaData;
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
        stop("WSAStartup failed");
    }

    int port;
    if (argc>1)
        port = atoi(argv[1]);
    else
        port=atoi(DEFAULT_PORT);
        
    sockets_struct sockets;

    if ( (sockets.py_sockfd=socket(AF_INET, SOCK_STREAM , 0)) == INVALID_SOCKET)
    {
        stop("socket");
    }

    sockets.py_sockaddr.sin_addr.s_addr = inet_addr(LOCAL);
    sockets.py_sockaddr.sin_family = AF_INET;
    sockets.py_sockaddr.sin_port = htons(port);
    
    if (connect(sockets.py_sockfd , (struct sockaddr *)&sockets.py_sockaddr , sizeof(sockets.py_sockaddr)) == SOCKET_ERROR)
    {
        stop("connect failed. Error");
        return 1;
    }

    HANDLE thread_SendToPy;
    if ((thread_SendToPy = CreateThread(NULL, 0, sendToPy, &sockets, 0, NULL)) == NULL)
        stop("CreateThread failed");

    recieveFromPy(sockets);

    if (TerminateThread(thread_SendToPy, 0) == 0)
        stop("TerminateThread failed"); 

    closesocket(sockets.py_sockfd);
    closesocket(sockets.player_sockfd);
    
    WSACleanup();

    return EXIT_SUCCESS;
}