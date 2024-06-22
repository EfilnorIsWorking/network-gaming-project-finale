#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <pthread.h>

#define PORT 12345
#define MAX_CLIENTS 10
#define BUFFER_SIZE 1024

// Structure pour passer le socket client et l'adresse IP
struct ClientInfo {
    int socket;
    char ip[INET_ADDRSTRLEN];
};

// Variables globales pour stocker les informations sur les clients
struct ClientInfo clients[MAX_CLIENTS];
int num_clients = 0;
pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;

// Déclarations de fonctions
void *client_handler(void *arg);
void broadcast_all_ip();
void* timer_thread(void* arg);
//void handle_clients();


void recepteur(void) {
    int server_socket;
    struct sockaddr_in server_addr;

    // Création du socket serveur
    if ((server_socket = socket(AF_INET, SOCK_STREAM, 0)) == -1) {
        perror("Échec de la création du socket");
        exit(EXIT_FAILURE);
    }

    // Configuration de l'adresse du serveur
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    server_addr.sin_port = htons(PORT);

    // Liaison du socket
    if (bind(server_socket, (struct sockaddr*)&server_addr, sizeof(server_addr)) == -1) {
        perror("Échec de la liaison");
        exit(EXIT_FAILURE);
    }

    // Écoute sur le port
    if (listen(server_socket, 5) == -1) {
        perror("Échec de l'écoute");
        exit(EXIT_FAILURE);
    }

    printf("Recepteur en écoute sur le port %d...\n", PORT);

    // Création du thread du minuteur
    pthread_t timer_tid;
    pthread_create(&timer_tid, NULL, timer_thread, NULL);

    while (1) {
        struct sockaddr_in client_addr;
        socklen_t client_addr_len = sizeof(client_addr);
        int client_socket = accept(server_socket, (struct sockaddr*)&client_addr, &client_addr_len);
        if (client_socket == -1) {
            perror("Échec de l'acceptation");
            continue;
        }

        // Ajout des informations sur le client à la variable globale
        pthread_mutex_lock(&mutex);
        if (num_clients < MAX_CLIENTS) {
            inet_ntop(AF_INET, &client_addr.sin_addr, clients[num_clients].ip, INET_ADDRSTRLEN);
            clients[num_clients].socket = client_socket;
            num_clients++;

            // Création du thread pour gérer le client
            pthread_t tid;
            pthread_create(&tid, NULL, client_handler, &client_socket);
        } else {
            printf("Trop de clients. Connexion rejetée.\n");
            close(client_socket);
        }
        pthread_mutex_unlock(&mutex);
    }

    // Fermeture du socket serveur
    close(server_socket);

}



// Fonction de traitement du client
void *client_handler(void *arg) {
    int client_socket = *((int*)arg);
    char buffer[BUFFER_SIZE];
    char user_input[BUFFER_SIZE];

    // Réception des messages envoyés par le client
    while (1) {
        ssize_t bytes_received = recv(client_socket, buffer, BUFFER_SIZE, 0);
        if (bytes_received <= 0) {
            pthread_mutex_lock(&mutex);
            // Fermeture de la connexion client et suppression du client de la variable globale
            for (int i = 0; i < num_clients; i++) {
                if (clients[i].socket == client_socket) {
                    printf("Déconnecté : %s\n", clients[i].ip);
                    close(client_socket);
                    for (int j = i; j < num_clients - 1; j++) {
                        clients[j] = clients[j + 1];
                    }
                    num_clients--;
                    break;
                }
            }
            pthread_mutex_unlock(&mutex);
            break;
        } 
        else {
                buffer[strlen(buffer)] = '\0';
                printf("Reçu : %s \n", buffer);
                //broadcast_message(buffer, client_socket);
            }
        }


    return NULL;
}

// Diffusion de l'adresse IP à tous les clients
void broadcast_all_ip () {

    char infoPacket[MAX_CLIENTS * INET_ADDRSTRLEN];
    memset(infoPacket, 0, sizeof(infoPacket));

    // 使用一个布尔数组来跟踪已经添加到infoPacket的IP地址
    int added[MAX_CLIENTS] = {0};

    // Parcourir le tableau des clients et ajouter chaque adresse IP au paquet d'informations
    for (int i = 0; i < num_clients; ++i) {
        // 检查是否已经添加过该IP地址
        if (!added[i]) {
            strcat(infoPacket, clients[i].ip);
            strcat(infoPacket, " "); // Ajouter un séparateur d'espace entre chaque adresse IP

            // 将该IP地址标记为已添加
            added[i] = 1;

            // 检查其他客户端是否具有相同的IP地址，并将它们标记为已添加
            for (int j = i + 1; j < num_clients; ++j) {
                if (strcmp(clients[i].ip, clients[j].ip) == 0) {
                    added[j] = 1;
                }
            }
        }
    }


    pthread_mutex_lock(&mutex);
    printf("Diffusion : %s \n", infoPacket);
    for (int i = 0; i <= num_clients; i++) {
        send(clients[i].socket, infoPacket, strlen(infoPacket), 0);
    }
    pthread_mutex_unlock(&mutex);
}

void* timer_thread(void* arg) {
    while (1) {
        sleep(1);
        broadcast_all_ip();
    }

    return NULL;
}

int main(){
    recepteur();
    return 0;
}