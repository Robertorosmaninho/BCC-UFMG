#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

#include <sys/types.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netinet/in.h>

#include "common.h"

#define BUFSZ 1024

void usage(int argc, char** argv) {
  printf("usage: %s <host> <first port> start\n", argv[0]);
  printf("example: %s 127.0.0.1 51511 start\n", argv[0]);
  exit(EXIT_FAILURE);
}

struct sockaddr_storage connect_server(const char* addrStr, int port) {
  struct sockaddr_storage serverAddr;
  memset(&serverAddr, 0, sizeof(serverAddr));

  if (0 != addrparse(addrStr, (uint16_t) port, &serverAddr)) {
    logexit("parse");
  }

  int socketClient;
  socketClient = socket(serverAddr.ss_family, SOCK_DGRAM, 0);
  if (socketClient == -1) {
    logexit("socket");
  }

  struct sockaddr* addr = (struct sockaddr*) (&serverAddr);
  if (0 != connect(socketClient, addr, sizeof(serverAddr))) {
    logexit("connect");
  }

  char* message = "connected\n";
  sendto(socketClient, (const char*) message, strlen(message), 0, 
        (const struct sockaddr*) &serverAddr, sizeof(serverAddr));
  
  char buffer[BUFSZ];
  int len;
  recvfrom(socketClient, (char*)buffer, sizeof(buffer), 0, 
           (struct sockaddr*)&serverAddr,(socklen_t *) &len);

  puts(buffer);
  close(socketClient);
  return serverAddr;
}

ServerSet set_servers(const char* addrStr, int port) {
  ServerSet serverSet;
  memset(&serverSet, 0, sizeof(serverSet));

  serverSet.serverAddr1 = connect_server(addrStr, port);
  serverSet.serverAddr2 = connect_server(addrStr, port+1);
  serverSet.serverAddr2 = connect_server(addrStr, port+2);
  serverSet.serverAddr3 = connect_server(addrStr, port+3);
  
  return serverSet;
}

int main(int argc, char** argv) {
  if (argc < 3) {
    usage(argc, argv);
  }
  
  ServerSet serverSet = set_servers(argv[1], atoi(argv[2]));
  

  exit(EXIT_SUCCESS);
}