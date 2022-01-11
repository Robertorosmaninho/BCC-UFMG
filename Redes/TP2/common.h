#pragma once

#include <arpa/inet.h>
#include <stdbool.h>
#include <stdlib.h>

struct ServerSet {
  struct sockaddr_storage serverAddr1;
  struct sockaddr_storage serverAddr2;
  struct sockaddr_storage serverAddr3;
  struct sockaddr_storage serverAddr4;
};

typedef struct ServerSet ServerSet;
void logexit(const char* msg);

int addrparse(const char* addrstr, uint16_t port, struct sockaddr_storage* storage);