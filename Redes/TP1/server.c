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

struct client_data {
  int csock;
  struct sockaddr_storage storage;
};

void* client_thread(void* data) {
  struct client_data* cdata = (struct client_data*) data;
  struct sockaddr* caddr = (struct sockaddr*) (&cdata->storage);

  char caddrstr[BUFSZ];
  addrtostr(caddr, caddrstr, BUFSZ);
  printf("[log] connection from %s\n", caddrstr);

  Pokedex pokedex = startPokedex();
  bool connection = true;

  while (connection) {
    char buf[BUFSZ], buf_temp[BUFSZ];
    memset(buf, 0, BUFSZ);
    
    unsigned int total = 0;
    size_t count = 0;
    bool receive_completed = false;

    while (!receive_completed) {
      count = recv(cdata->csock, buf_temp, BUFSZ - 1, 0);
      total += count;

      for (int i = total - count, j = 0; i < total; i++, j++)
        buf[i] = buf_temp[j];

      if (count == 0) {
        connection = false;
        break;
      }

      for (int i = 0; i < total; i++) {
        if (buf[i] == '\n') {
          receive_completed = true;
          break;
        }
      }

      // printf("[debug] incomplete msg, waiting for '\\n'\n");
      // printf("[debug] buf: %s\n", buf);
    }
    printf("[msg] %s, %d bytes: %s", caddrstr, (int) count, buf);

    char msg[BUFSZ] = "";
    if (selectCommand(buf, &pokedex, msg)) {
      deletePokedex(&pokedex);
      logexit("kill");
    }
    // printf("Passou aqui!\n");
    strcat(msg, "\n");
    count = send(cdata->csock, msg, strlen(msg), 0);
    if (count != strlen(msg)) {
      logexit("send");
    }
    // printf("Passou aqui também!\n");
  }
  close(cdata->csock);
  pthread_exit(EXIT_SUCCESS);
}

int main(int argc, char** argv) {
  if (argc < 3) {
    usage(argc, argv);
  }

  struct sockaddr_storage storage;
  if (0 != server_sockaddr_init(argv[1], argv[2], &storage)) {
    usage(argc, argv);
  }

  int s;
  s = socket(storage.ss_family, SOCK_STREAM, 0);
  if (s == -1) {
    logexit("socket");
  }

  int enable = 1;
  if (0 != setsockopt(s, SOL_SOCKET, SO_REUSEADDR, &enable, sizeof(int))) {
    logexit("setsockopt");
  }

  struct sockaddr* addr = (struct sockaddr*) (&storage);
  if (0 != bind(s, addr, sizeof(storage))) {
    logexit("bind");
  }

  if (0 != listen(s, 10)) {
    logexit("listen");
  }

  char addrstr[BUFSZ];
  addrtostr(addr, addrstr, BUFSZ);
  printf("bound to %s, waiting connections\n", addrstr);

  while (1) {
    struct sockaddr_storage cstorage;
    struct sockaddr* caddr = (struct sockaddr*) (&cstorage);
    socklen_t caddrlen = sizeof(cstorage);

    int csock = accept(s, caddr, &caddrlen);
    if (csock == -1) {
      logexit("accept");
    }

    struct client_data* cdata = malloc(sizeof(*cdata));
    if (!cdata) {
      logexit("malloc");
    }

    cdata->csock = csock;
    memcpy(&(cdata->storage), &cstorage, sizeof(cstorage));

    pthread_t tid;
    client_thread(cdata);
    pthread_create(&tid, NULL, client_thread, cdata);
  }

  exit(EXIT_SUCCESS);
}