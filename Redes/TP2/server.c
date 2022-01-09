#include "common.h"

#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include <sys/socket.h>
#include <sys/types.h>

#define BUFSZ 1024

void usage(int argc, char** argv) {
  printf("usage: %s <v4|v6> <server port>\n", argv[0]);
  printf("example: %s v4 51511\n", argv[0]);
  exit(EXIT_FAILURE);
}

int main(int argc, char** argv) {
  if (argc < 3) {
    usage(argc, argv);
  }

  struct sockaddr_storage serverAddr, clientAddr;
  if (0 != server_sockaddr_init(argv[1], argv[2], &serverAddr)) {
    usage(argc, argv);
  }

  int s;
  s = socket(serverAddr.ss_family, SOCK_DGRAM, 0);
  if (s == -1) {
    logexit("socket");
  }

  struct sockaddr* addr = (struct sockaddr*) (&serverAddr);
  if (0 != bind(s, addr, sizeof(serverAddr))) {
    logexit("bind");
  }

  //receive the datagram
  int len;
  len = sizeof(clientAddr);

  //receive message from server
  char buf[BUFSZ];
  struct sockaddr* client = (struct sockaddr*) (&clientAddr);
  int n = recvfrom(s, buf, sizeof(buf), 0, client, (socklen_t *)&len); 

  // message
  buf[n] = '\0';
  puts(buf);

  char *message = "bound and waiting connections\n";

  // send the response
  sendto(s, message, 1000, 0, client, sizeof(clientAddr));
  
  exit(EXIT_SUCCESS);
}