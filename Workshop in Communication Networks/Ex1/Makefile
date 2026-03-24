CC = gcc
CFLAGS = -Wall -Wextra -O2 -std=c99
LDFLAGS =

# List of source files
COMMON_SRC = mutual_server_client.c

# Targets
all: server client

server: server.c server.h $(COMMON_SRC) mutual_server_client.h
	$(CC) $(CFLAGS) -o server server.c $(COMMON_SRC) $(LDFLAGS)

client: client.c client.h $(COMMON_SRC) mutual_server_client.h
	$(CC) $(CFLAGS) -o client client.c $(COMMON_SRC) $(LDFLAGS)

clean:
	rm -f server client
