#pragma once

#include <arpa/inet.h>
#include <stdbool.h>
#include <stdlib.h>

void logexit(const char* msg);

int addrparse(const char* addrstr, const char* portstr, struct sockaddr_storage* storage);

void addrtostr(const struct sockaddr* addr, char* str, size_t strsize);

int server_sockaddr_init(const char* proto, const char* portstr, struct sockaddr_storage* storage);

// Definção de um nó na lista simplesmente encadeada
struct Node {
  char name[15];
  struct Node* next;
};

// Definição do tipo Pokemon como um Node
typedef struct Node* Pokemon;

struct PokemonList {
  Pokemon pokemon;
  int size;
};

// Definição do tipo Pokedex como uma lista de pokemons
typedef struct PokemonList Pokedex;

// Inicia a pokedex vazia
Pokedex startPokedex();

// Insere o pokemon na pokedex caso ele não exista, incrementa o tamanho da lista e retorna
// verdadeiro Se o pokemon já existir na lista, então retorna falso!
bool insertPokemon(Pokedex* pokedex, Pokemon pokemon);

// Lista os pokemons em uma unica string separados por espaço e com \n no final
void listPokemon(Pokedex* pokedex, char* pokemons);

void addPokemon(char* command, Pokedex* pokedex, char* result);

void removePokemon(char* command, Pokedex* pokedex, char* result);

void exchangePokemon(char* command, Pokedex* pokedex, char* result);

int selectCommand(char* command, Pokedex* pokedex, char* result);

void deletePokemon(Pokemon* pokemon);

void deletePokedex(Pokedex* pokedex);

void printList(Pokemon pokemon);

bool findOnPokedex(Pokedex* pokedex, char* pokemonName);

bool stringValidator(char* command);