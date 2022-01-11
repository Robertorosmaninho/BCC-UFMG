#include "common.h"

#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include <sys/socket.h>
#include <sys/types.h>

#define BUFSZ 1024
#define NUM_SOCKETS 4

void usage(int argc, char** argv) {
  printf("usage: %s <v4|v6> <server port>\n", argv[0]);
  printf("example: %s v4 51511\n", argv[0]);
  exit(EXIT_FAILURE);
}

struct server_data {
  int sock;
  int path_num;
  int port;
  const char* protocol;
  struct sockaddr* client;
  socklen_t clientSize;
  struct sockaddr_storage serverAddr;
};

int connect_server(int port) {
  int udpfd;
  struct sockaddr_in servaddr;

  printf("Abrindo porta %u\n", (uint16_t) port);
  bzero(&servaddr, sizeof(servaddr));
  servaddr.sin_family = AF_INET;
  servaddr.sin_addr.s_addr = htonl(INADDR_ANY);
  servaddr.sin_port = htons(port);

  /* create UDP socket */
  udpfd = socket(AF_INET, SOCK_DGRAM, 0);

  // binding server addr structure to udp sockfd
  bind(udpfd, (struct sockaddr*) &servaddr, sizeof(servaddr));

  return udpfd;
}

int recv_send(struct sockaddr_in cliaddr, int udpfd, int i, int firstRead) {
  char message[BUFSZ];
  sprintf(message, "game started: path %d", i+1);
  char buffer[BUFSZ];
  int len = sizeof(cliaddr);

  printf("\nMessage from UDP client: ");
  bzero(buffer, sizeof(buffer));

  recvfrom(udpfd, buffer, sizeof(buffer), 0, (struct sockaddr*) &cliaddr, (socklen_t *) &len);
  puts(buffer);
  firstRead = 1;

  sendto(udpfd,
         (const char*) message,
         sizeof(buffer),
         0,
         (struct sockaddr*) &cliaddr,
         sizeof(cliaddr));
  
  return firstRead;
}

int main(int argc, char** argv) {
  if (argc < 3) {
    usage(argc, argv);
  }

  int nready, maxfdp1;
  int udpfd[NUM_SOCKETS];
  int firstRead = 0;
  fd_set rset;
  struct sockaddr_in cliaddr;

  void sig_chld(int);

  int port = atoi(argv[2]);

  for (int i = 0; i < NUM_SOCKETS; i++)
    udpfd[i] = connect_server(port + i);  // 9000 + i

  // get maxfd
  maxfdp1 = FD_SETSIZE;

  // clear the descriptor set
  FD_ZERO(&rset);

  while (1) {
    // set listenfd and udpfd in readset
    for (int i = 0; i < NUM_SOCKETS; i++)
      FD_SET(udpfd[i], &rset);

    // select the ready descriptor
    nready = select(maxfdp1, &rset, NULL, NULL, NULL);
    if (nready < 0)
      printf("select error");

    // if udp socket is readable receive the message.
    for (int i = 0; i < NUM_SOCKETS; i++) {
      if (FD_ISSET(udpfd[i], &rset))
        firstRead = recv_send(cliaddr, udpfd[i], i, firstRead);
    }
  }

  exit(EXIT_SUCCESS);
}