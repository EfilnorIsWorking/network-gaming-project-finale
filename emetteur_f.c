#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <ctype.h>

#define PORT 12345
#define MAX_BUFFER_SIZE 1024
#define MAX_IP_COUNT 100
#define MAX_IP_LENGTH 20 // Assuming maximum IP length is 20 characters

void stop(const char *message) {
    perror(message);
    exit(EXIT_FAILURE);
}

void removeNonNumeric(char *str) {
    int i, j;
    for (i = 0, j = 0; str[i] != '\0'; i++) {
        if (isdigit(str[i]) || str[i] == '.') {
            str[j++] = str[i];
        }
    }
    str[j] = '\0';
}

void emetteur (const char *message, const char *serverIP) {
    struct sockaddr_in serverAddress;
    serverAddress.sin_family = AF_INET;
    serverAddress.sin_addr.s_addr = inet_addr(serverIP);
    serverAddress.sin_port = htons(PORT);

    int clientSocket = socket(AF_INET, SOCK_STREAM, 0);
    if (clientSocket == -1) {
        stop("Erreur lors de la création de la socket ");
    }

    if (connect(clientSocket, (struct sockaddr *)&serverAddress, sizeof(serverAddress)) == -1) {
        stop("Erreur lors de la connexion");
    }

    int ipCount = 0;
    char ipList[MAX_IP_COUNT][MAX_IP_LENGTH];

    // Send the message to the server
    if (send(clientSocket, message, strlen(message), 0) == -1) {
        perror("Erreur lors de l'envoi du message");
        close(clientSocket);
        return;
    }

    // Receive the IP list from the server
    char receivedIPList[MAX_BUFFER_SIZE]; // Buffer to store received IP list
    int bytes_received = recv(clientSocket, receivedIPList, sizeof(receivedIPList), 0);
    if (bytes_received == -1) {
        stop("Erreur lors de la réception de la liste d'IP");
    } else if (bytes_received == 0) {
        printf("Le serveur a fermé la connexion.\n");
        close(clientSocket);
        return;
    }

    char *token = strtok(receivedIPList, " ");
    while (token != NULL) {
        removeNonNumeric(token);
        // Check if the IP address is valid
        // Check if the IP address already exists in the list
        int isDuplicate = 0;
        for (int i = 0; i < ipCount; ++i) {
            if (strcmp(ipList[i], token) == 0) {
                isDuplicate = 1;
                break;
            }
        }

        if (!isDuplicate) {
            // If the IP address is not a duplicate and valid, store it in the list
            if (ipCount >= MAX_IP_COUNT) {
                printf("La liste d'IP est pleine.\n");
                break;
            }
            strcpy(ipList[ipCount], token);
            ipCount++;
        }
        token = strtok(NULL, " ");
    }

    printf("IP List:\n");
    for (int i = 0; i < ipCount; ++i) {
        printf("%s\n", ipList[i]);
    }

    // Send data to each IP address in the list
    for (int i = 0; i < ipCount; ++i) {
        struct sockaddr_in serverAddress;
        serverAddress.sin_family = AF_INET;
        serverAddress.sin_addr.s_addr = inet_addr(ipList[i]);
        serverAddress.sin_port = htons(PORT);

        // Create a new socket to connect to the current IP address
        int currentSocket = socket(AF_INET, SOCK_STREAM, 0);
        if (currentSocket == -1) {
            perror("Erreur lors de la création de la socket ");
            continue; // Try connecting to the next IP address
        }

        // Connect to the current IP address
        if (connect(currentSocket, (struct sockaddr *)&serverAddress, sizeof(serverAddress)) == -1) {
            perror("Erreur lors de la connexion");
            close(currentSocket); // Close the current socket
            continue; // Try connecting to the next IP address
        }

        printf("Connecté à l'adresse IP : %s\n", ipList[i]);

        // Send data to the server
        if (send(currentSocket, message, strlen(message), 0) == -1) {
            perror("Erreur lors de l'envoi du paquet");
        } else {
            printf("Paquet envoyé avec succès au serveur %s\n", ipList[i]);
        }

        // Close the current socket
        close(currentSocket);
    }
}

int main(int argc, char **argv) {
    if (argc != 3) {
        fprintf(stderr, "Usage: %s <Server IP> <Message>\n", argv[0]);
        exit(EXIT_FAILURE);
    }

    char *SERVER_IP = argv[1];
    char *message = argv[2];
    while(1){

        emetteur(message, SERVER_IP);
        sleep(2);
    }
    

    return 0;
}
