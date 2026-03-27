#ifndef _SERVER_H_
#define _SERVER_H_

#include "mutual_server_client.h"
#define NUM_OF_CLIENTS 1

/**
 * Establishes a server socket listening on the specified port.
 * @param port_num The port number on which the server listens.
 * @return The file descriptor of the listening socket.
 * On failure, exits the program with an error.
 */
int establish_server_socket(unsigned short port_num);

/**
 * Accepts a client connection on the listening socket.
 *
 * @param listen_fd_ptr Pointer to the variable holding the listen socket fd;
 *        it will be set by this function.
 * @param conn_fd_ptr Pointer to the variable where accepted connection fd will be stored.
 * On failure, exits the program with an error.
 */
void accept_conn_with_client(int *listen_fd_ptr, int *conn_fd_ptr);

/**
 * Receives 'n' packets of size 'packet_size' from a connected socket.
 * @param conn_fd Connected socket file descriptor.
 * @param listen_fd Listening socket file descriptor (for cleanup).
 * @param recv_buffer Buffer to store received data.
 * @param packet_size Number of bytes to receive per packet.
 * @param n Number of packets to receive.
 * On failure, exits the program with an error.
 */
void recv_n_packets(int conn_fd, int listen_fd, char *recv_buffer, int
packet_size, int n);

/**
 * Sends an acknowledgment message to the connected client.
 *
 * @param conn_fd Connected socket file descriptor.
 * @param listen_fd Listening socket file descriptor (for cleanup).
 * @param recv_buffer Buffer pointer (used for cleanup if send fails).
 * On failure, exits the program with an error.
 */
void send_ack(int conn_fd, int listen_fd, char *recv_buffer);

/**
 * Receives packets for exponentially increasing packet sizes,
 * For each packet size, receives warmup packets plus measured packets,
 * then sends an acknowledgment to the client.
 * @param conn_fd Connected socket file descriptor.
 * @param listen_fd Listening socket file descriptor (for cleanup).
 */
void recv_packets_for_diff_packet_sizes(int conn_fd, int listen_fd);
#endif //_SERVER_H_
