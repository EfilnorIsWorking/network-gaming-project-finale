#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>

#define PORT 8080
#define FILENAME "/home/delong/net/delong_c/GameControl/testdata.json"


void send_client() {

    int client_socket, n;
    struct sockaddr_in server_address;
    FILE *file;
    char buffer[10240];
    sleep(10);
    // Create a TCP/IP socket
    client_socket = socket(AF_INET, SOCK_STREAM, 0);
    if (client_socket < 0) {
        perror("Error opening socket");
        exit(1);
    }

    // Connect to the server
    server_address.sin_family = AF_INET;
    server_address.sin_port = htons(PORT);
    server_address.sin_addr.s_addr = inet_addr("127.0.0.1");
    if (connect(client_socket, (struct sockaddr *) &server_address, sizeof(server_address)) < 0) {
        perror("Error connecting");
        exit(1);
    }

    while (1) {
        // Send file data
        file = fopen("/home/delong/net/delong_c/GameControl/testdata.json", "rb");
        if (file == NULL) {
            perror("Error opening file");
            exit(1);
        }
        bzero(buffer, 10240);
        n = fread(buffer, 1, sizeof(buffer), file);
        if (n < 0) {
            perror("Error reading file");
            exit(1);
        }
        fclose(file);

        n = send(client_socket, buffer, n, 0);
        if (n < 0) {
            perror("Error writing to socket");
            exit(1);
        }
        printf("File sent: testdata.json\n");
        sleep(1);
    }
    close(client_socket);
}

int main() {
    send_client();
    return 0;
}