#include "common.h"

#include <ctype.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <arpa/inet.h>

void logexit(const char* msg) {
  perror(msg);
  exit(EXIT_FAILURE);
}

int addrparse(const char* addrStr, uint16_t port, struct sockaddr_storage* serverAddr) {
  if (addrStr == NULL || port == 0) {
    return -1;
  }

  port = htons(port);  // host to network short

  struct in_addr inaddr4;  // 32-bit IP address
  if (inet_pton(AF_INET, addrStr, &inaddr4)) {
    struct sockaddr_in* addr4 = (struct sockaddr_in*) serverAddr;
    addr4->sin_family = AF_INET;
    addr4->sin_port = port;
    addr4->sin_addr = inaddr4;
    return 0;
  }

  struct in6_addr inaddr6;  // 128-bit IPv6 address
  if (inet_pton(AF_INET6, addrStr, &inaddr6)) {
    struct sockaddr_in6* addr6 = (struct sockaddr_in6*) serverAddr;
    addr6->sin6_family = AF_INET6;
    addr6->sin6_port = port;
    // addr6->sin6_addr = inaddr6
    memcpy(&(addr6->sin6_addr), &inaddr6, sizeof(inaddr6));
    return 0;
  }

  return -1;
}