#pragma once

#include <arpa/inet.h>
#include <stdbool.h>
#include <stdlib.h>

#define NUM_SOCKETS 4

struct ServerSet {
  struct sockaddr_storage serverAddr[NUM_SOCKETS];
  int socketClient[NUM_SOCKETS];
};

typedef struct ServerSet ServerSet;
void logexit(const char* msg);

int addrparse(const char* addrstr, uint16_t port, struct sockaddr_storage* storage);