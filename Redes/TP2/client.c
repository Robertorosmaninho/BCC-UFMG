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

int main(int argc, char** argv) {
  if (argc < 3) {
    usage(argc, argv);
  }

  struct sockaddr_storage serverAddr;
  if (0 != addrparse(argv[1], argv[2], &serverAddr)) {
    usage(argc, argv);
  }

  int s;
  s = socket(serverAddr.ss_family, SOCK_DGRAM, 0);
  if (s == -1) {
    logexit("socket");
  }

  struct sockaddr* addr = (struct sockaddr*) (&serverAddr);
  if (0 != connect(s, addr, sizeof(serverAddr))) {
    logexit("connect");
  }

  // request to send datagram
  // no need to specify server address in sendto
  // connect stores the peers IP and port
  char* message = "connected\n";
  sendto(s, message, 1000, 0, (struct sockaddr*)NULL, sizeof(serverAddr));
      
  // waiting for response
  char buf[BUFSZ];
  recvfrom(s, buf, sizeof(buf), 0, (struct sockaddr*)NULL, NULL);
  puts(buf);
  
  // close the descriptor
  close(s);
}