#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>

#define PORT 8090
#define BUFFER_SIZE 10240
#define FILE_PATH "GameControl/testdata1.json"

void error(const char *msg) {
    perror(msg);
    exit(1);
}

int main() {
    int server_socket, connection_socket;
    struct sockaddr_in server_addr, client_addr;
    socklen_t client_len;
    char buffer[BUFFER_SIZE];
    FILE *file;
    
    // 创建一个TCP/IP套接字
    server_socket = socket(AF_INET, SOCK_STREAM, 0);
    if (server_socket < 0) {
        error("ERROR opening socket");
    }

    // 初始化服务器地址结构
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = inet_addr("127.0.0.1");
    server_addr.sin_port = htons(PORT);

    // 绑定套接字到端口
    if (bind(server_socket, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        close(server_socket);
        error("ERROR on binding");
    }

    // 监听传入的连接
    listen(server_socket, 1);

    printf("等待连接...\n");

    while (1) {
        client_len = sizeof(client_addr);
        connection_socket = accept(server_socket, (struct sockaddr *)&client_addr, &client_len);
        if (connection_socket < 0) {
            error("ERROR on accept");
        }

        // 接收文件数据并保存到文件中
        

        printf("连接已建立，接收数据...\n");

        

        while (1) {

            file = fopen(FILE_PATH, "wb");
            if (file == NULL) {
                close(connection_socket);
                error("ERROR opening file");
            }

            // 接收数据
            int bytes_received = recv(connection_socket, buffer, BUFFER_SIZE, 0);
            if (bytes_received < 0) {
                fclose(file);
                close(connection_socket);
                error("ERROR reading from socket");
            }
            if (bytes_received == 0) {
                error("ERROR recerve from socket");
                break;
            }

            // 将接收到的数据写入文件
            if (fwrite(buffer, 1, bytes_received, file) != bytes_received) {
                fclose(file);
                close(connection_socket);
                error("ERROR writing to file");
            }

            printf("从客户端接收的文件已保存为：%s\n", FILE_PATH);

            fclose(file);
            sleep(1);
        }

                    // 关闭文件和连接
        
        close(connection_socket);

        printf("连接已关闭，等待新的连接...\n");
    }

    // 关闭服务器套接字
    close(server_socket);

    return 0;
}
