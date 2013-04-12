CC = gcc
CFLAGS = -Wall
LIBS = -luuid


main2: waldo_foreign.c
	gcc -c $(CFLAGS) -fPIC waldo_foreign.c
	gcc -shared waldo_foreign.o $(LIBS) -o waldo_foreign.so