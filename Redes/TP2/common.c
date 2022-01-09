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

int addrparse(const char* addrStr, const char* portStr, struct sockaddr_storage* serverAddr) {
  if (addrStr == NULL || portStr == NULL) {
    return -1;
  }

  uint16_t port = (uint16_t) atoi(portStr);  // unsigned short
  if (port == 0) {
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

int server_sockaddr_init(const char* protocol,
                         const char* portStr,
                         struct sockaddr_storage* serverAddr) {
  uint16_t port = (uint16_t) atoi(portStr);  // unsigned short
  if (port == 0) {
    return -1;
  }
  port = htons(port);  // host to network short

  memset(serverAddr, 0, sizeof(*serverAddr));
  if (0 == strcmp(protocol, "v4")) {
    struct sockaddr_in* addr4 = (struct sockaddr_in*) serverAddr;
    addr4->sin_family = AF_INET;
    addr4->sin_addr.s_addr = INADDR_ANY;
    addr4->sin_port = port;
    return 0;
  } else if (0 == strcmp(protocol, "v6")) {
    struct sockaddr_in6* addr6 = (struct sockaddr_in6*) serverAddr;
    addr6->sin6_family = AF_INET6;
    addr6->sin6_addr = in6addr_any;
    addr6->sin6_port = port;
    return 0;
  } else {
    return -1;
  }
}