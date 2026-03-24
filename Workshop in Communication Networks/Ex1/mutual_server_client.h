#ifndef _MUTUAL_SERVER_CLIENT_H_
#define _MUTUAL_SERVER_CLIENT_H_

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <netinet/in.h>

#define SERVER_PORT 12346
#define MAX_PACKET_SIZE (1024 * 1024)
#define DATA_TOTAL_BYTES (16 * MAX_PACKET_SIZE)
#define ACK_MSG "OK"
#define ACK_BYTES 2

/**
 * Frees the given buffer (if not NULL), closes the given file descriptors (if
 * valid), prints the error message, and exits the program.
 * @param fd1 First file descriptor to close (if >= 0)
 * @param fd2 Second file descriptor to close (if >= 0)
 * @param buff Pointer to buffer to free (can be NULL)
 * @param msg Error message to print using perror
 */
void cleanup_and_exit(int fd1, int fd2, char *buff, const char *msg);

/**
 * Creates a TCP socket and returns its file descriptor.
 * Exits on failure.
 * @return File descriptor of the created socket
 */
int create_socket(void);

/**
 * Allocates a buffer of the given packet size.
 * On failure, cleans up the provided file descriptors and exits.
 * @param fd1 First file descriptor to close on error
 * @param fd2 Second file descriptor to close on error
 * @param packet_size Size of the buffer to allocate (in bytes)
 * @return Pointer to the allocated buffer
 */
char *create_buffer(int fd1, int fd2, int packet_size);

/*
 * Choice of warmup cycles:
 * Small packets are more sensitive to startup effects (like TCP slow start),
 * so more warmup cycles help stabilize throughput. Large packets stabilize
 * quickly and need fewer warmup cycles to avoid overhead.
 */
/**
 * Returns the number of warmup cycles to use for a given packet size.
 * @param packet_size Size of the packet (in bytes)
 * @return Number of warmup cycles to perform
 */
int get_num_warmup_cycles(int packet_size);

#endif //_MUTUAL_SERVER_CLIENT_H_
