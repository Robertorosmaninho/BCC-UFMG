all: build

build:
	g++ -Wall -c reader.cpp main.cpp
	g++ -Wall reader.o -o reader
	g++ -Wall main.o -lpthread -o prog

clean:
	rm reader.o main.o reader prog

run:
	./reader < in2.txt | ./prog 5 10