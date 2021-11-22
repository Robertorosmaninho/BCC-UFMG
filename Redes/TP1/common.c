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

int addrparse(const char* addrstr, const char* portstr, struct sockaddr_storage* storage) {
  if (addrstr == NULL || portstr == NULL) {
    return -1;
  }

  uint16_t port = (uint16_t) atoi(portstr);  // unsigned short
  if (port == 0) {
    return -1;
  }
  port = htons(port);  // host to network short

  struct in_addr inaddr4;  // 32-bit IP address
  if (inet_pton(AF_INET, addrstr, &inaddr4)) {
    struct sockaddr_in* addr4 = (struct sockaddr_in*) storage;
    addr4->sin_family = AF_INET;
    addr4->sin_port = port;
    addr4->sin_addr = inaddr4;
    return 0;
  }

  struct in6_addr inaddr6;  // 128-bit IPv6 address
  if (inet_pton(AF_INET6, addrstr, &inaddr6)) {
    struct sockaddr_in6* addr6 = (struct sockaddr_in6*) storage;
    addr6->sin6_family = AF_INET6;
    addr6->sin6_port = port;
    // addr6->sin6_addr = inaddr6
    memcpy(&(addr6->sin6_addr), &inaddr6, sizeof(inaddr6));
    return 0;
  }

  return -1;
}

void addrtostr(const struct sockaddr* addr, char* str, size_t strsize) {
  int version;
  char addrstr[INET6_ADDRSTRLEN + 1] = "";
  uint16_t port;

  if (addr->sa_family == AF_INET) {
    version = 4;
    struct sockaddr_in* addr4 = (struct sockaddr_in*) addr;
    if (!inet_ntop(AF_INET, &(addr4->sin_addr), addrstr, INET6_ADDRSTRLEN + 1)) {
      logexit("ntop");
    }
    port = ntohs(addr4->sin_port);  // network to host short
  } else if (addr->sa_family == AF_INET6) {
    version = 6;
    struct sockaddr_in6* addr6 = (struct sockaddr_in6*) addr;
    if (!inet_ntop(AF_INET6, &(addr6->sin6_addr), addrstr, INET6_ADDRSTRLEN + 1)) {
      logexit("ntop");
    }
    port = ntohs(addr6->sin6_port);  // network to host short
  } else {
    logexit("unknown protocol family.");
  }
  if (str) {
    snprintf(str, strsize, "IPv%d %s %hu", version, addrstr, port);
  }
}

int server_sockaddr_init(const char* proto,
                         const char* portstr,
                         struct sockaddr_storage* storage) {
  uint16_t port = (uint16_t) atoi(portstr);  // unsigned short
  if (port == 0) {
    return -1;
  }
  port = htons(port);  // host to network short

  memset(storage, 0, sizeof(*storage));
  if (0 == strcmp(proto, "v4")) {
    struct sockaddr_in* addr4 = (struct sockaddr_in*) storage;
    addr4->sin_family = AF_INET;
    addr4->sin_addr.s_addr = INADDR_ANY;
    addr4->sin_port = port;
    return 0;
  } else if (0 == strcmp(proto, "v6")) {
    struct sockaddr_in6* addr6 = (struct sockaddr_in6*) storage;
    addr6->sin6_family = AF_INET6;
    addr6->sin6_addr = in6addr_any;
    addr6->sin6_port = port;
    return 0;
  } else {
    return -1;
  }
}

Pokemon cretePokemon(char* pokemonName) {
  Pokemon pokemon = (Pokemon) malloc(sizeof(Pokemon));
  sprintf(pokemon->name, "%s", pokemonName);
  pokemon->next = NULL;

  return pokemon;
}

// Inicia a pokedex vazia
Pokedex startPokedex() {
  Pokedex* pokedex = malloc(sizeof(Pokedex));
  pokedex->pokemon = NULL;
  pokedex->size = 0;

  return *pokedex;
}

// Insere o pokemon na pokedex caso ele não exista, incrementa o tamanho da lista e retorna
// verdadeiro Se o pokemon já existir na lista, então retorna falso!
bool insertPokemon(Pokedex* pokedex, Pokemon pokemon) {
  // Lista vazia
  if (pokedex->pokemon == NULL) {
    // printf("[debug] insert %s in empty list\n", pokemon->name);
    pokedex->pokemon = pokemon;
    pokedex->size = 1;
    return true;
  }

  // Lista não vazia
  Pokemon temp = pokedex->pokemon;
  // printf("[debug] list add: ");
  // printList(temp);
  // printf("\n");
  while (temp->next != NULL) {
    // printf("[debug] insert comparasion (%s ?= %s)\n", temp->name, pokemon->name);
    if (!strncmp(temp->name, pokemon->name, strlen(pokemon->name)))
      return false;
    temp = temp->next;
  }

  // Previne o segundo elemento de ser igual ao primeiro
  // printf("[debug] insert 2nd comparasion (%s ?= %s)\n", temp->name, pokemon->name);
  if (!strncmp(temp->name, pokemon->name, strlen(pokemon->name)))
    return false;

  temp->next = pokemon;
  pokedex->size++;
  return true;
}

// Lista os pokemons em uma unica string separados por espaço e com \n no final
void listPokemon(Pokedex* pokedex, char* result) {
  if (pokedex->pokemon == NULL) {
    sprintf(result, "none");
    return;
  }

  Pokemon temp = pokedex->pokemon;
  sprintf(result, temp->name);
  temp = temp->next;

  while (temp != NULL) {
    strcat(result, " ");
    strcat(result, temp->name);
    temp = temp->next;
  }
}

void addPokemon(char* command, Pokedex* pokedex, char* result) {
  char* tokens = strtok(command, " ");

  if (strlen(tokens) > 10) {
    sprintf(result, "invalid message");
    return;
  }

  while (tokens != NULL) {
    Pokemon pokemon = cretePokemon(tokens);

    if (pokedex->size == 40) {
      strcat(result, "limit exceeded");
      return;
    }

    if (insertPokemon(pokedex, pokemon)) {
      strcat(result, tokens);
      strcat(result, " added");
    } else {
      strcat(result, tokens);
      strcat(result, " already exists");
    }
    tokens = strtok(NULL, " ");
    if (tokens != NULL)
      strcat(result, " ");
  }
}

void removePokemon(char* command, Pokedex* pokedex, char* result) {
  char* tokens = strtok(command, " ");

  if (strlen(tokens) > 10) {
    sprintf(result, "invalid message");
    return;
  }

  while (tokens != NULL) {
    if (findOnPokedex(pokedex, tokens)) {
      Pokemon current = pokedex->pokemon;
      Pokemon next = NULL;

      // 1 da lista
      if (!strncmp(tokens, current->name, strlen(current->name))) {
        pokedex->pokemon = current->next;
        free(current);
      } else {
        // 2 em diante
        while (current->next != NULL) {
          if (!strncmp(tokens, current->next->name, strlen(current->next->name))) {
            next = current->next;
            current->next = next->next;
            free(next);
            break;
          }
          current = current->next;
        }
      }

      strcat(result, tokens);
      strcat(result, " removed");
    } else {
      strcat(result, tokens);
      strcat(result, " does not exist");
    }
    tokens = strtok(NULL, " ");
    if (tokens != NULL)
      strcat(result, " ");
  }
}

void exchangePokemon(char* command, Pokedex* pokedex, char* result) {
  char* tokens = strtok(command, " ");
  char pokemon1[15];
  sprintf(pokemon1, "%s", tokens);

  if (strlen(pokemon1) > 10) {
    sprintf(result, "invalid message");
    return;
  }

  if (!findOnPokedex(pokedex, pokemon1)) {
    sprintf(result, "%s", pokemon1);
    strcat(result, " does not exist");
    return;
  }

  tokens = strtok(NULL, " ");
  char pokemon2[15];
  sprintf(pokemon2, "%s", tokens);

  if (strlen(pokemon2) > 10) {
    sprintf(result, "invalid message");
    return;
  }

  if (findOnPokedex(pokedex, pokemon2)) {
    sprintf(result, "%s", pokemon2);
    strcat(result, " already exists");
    return;
  }

  Pokemon temp = pokedex->pokemon;
  while (temp != NULL) {
    if (strncmp(temp->name, pokemon1, strlen(pokemon1)) == 0) {
      sprintf(temp->name, pokemon2);
      sprintf(result, "%s", pokemon1);
      strcat(result, " exchanged");
      return;
    }
    temp = temp->next;
  }

  logexit("exchange");
}

int selectCommand(char* command, Pokedex* pokedex, char* result) {
  command = strtok(command, "\n");
  printf("command: %s\n", command);
  if (!stringValidator(command)) {
    sprintf(result, "invalid message");
    return 0;
  }

  if (strncmp("add", command, 3) == 0) {
    addPokemon(command + 4, pokedex, result);
    // printf("[debug] add pokemon: %s\n", result);
  } else if (strncmp("remove", command, 6) == 0)
    removePokemon(command + 7, pokedex, result);
  else if (strncmp("exchange", command, 8) == 0)
    exchangePokemon(command + 9, pokedex, result);
  else if (strncmp("list", command, 4) == 0) {
    listPokemon(pokedex, result);
    // printf("[debug] list: %s\n", result);
  } else {
    printf("mismatch pattern\n");
    return -1;
  }
  return 0;
}

void deletePokemon(Pokemon* pokemon) {
  Pokemon current = *pokemon;
  Pokemon next;

  while (current != NULL) {
    next = current->next;
    free(current);
    current = next;
  }

  pokemon = NULL;
}

void deletePokedex(Pokedex* pokedex) {
  deletePokemon(&pokedex->pokemon);
  pokedex = NULL;
}

void printList(Pokemon pokemon) {
  while (pokemon != NULL) {
    printf(" %s ", pokemon->name);
    pokemon = pokemon->next;
  }
}

bool findOnPokedex(Pokedex* pokedex, char* pokemonName) {
  Pokemon pokemon = pokedex->pokemon;

  while (pokemon != NULL) {
    // printf("[debug] comparing on find (%s ?= %s)\n", pokemon->name, pokemonName);
    if (!strncmp(pokemonName, pokemon->name, strlen(pokemon->name)))
      return true;
    pokemon = pokemon->next;
  }

  return false;
}

bool stringValidator(char* command) {
  for (int i = 0; i < strlen(command); i++) {
    if ((command[i] >= 97 && command[i] <= 122) || command[i] == 32 ||
        (command[i] >= 48 && command[i] <= 57))
      continue;
    else
      return false;
  }
  return true;
}