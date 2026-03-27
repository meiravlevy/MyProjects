#ifndef _CLIENT_H_
#define _CLIENT_H_

#include "mutual_server_client.h"
#include <arpa/inet.h>
#include <sys/time.h>

/**
 * Establishes a TCP connection to the given server IP and returns the socket
 * fd. Exits the program if any step fails.
 * @param server_ip The server IP address as a string
 * @return File descriptor of the connected client socket
 */
int establish_client_socket(const char *server_ip);

/**
 * Sends n packets of the given size using the provided buffer.
 * Exits on error.
 *
 * @param conn_fd Connected socket file descriptor
 * @param buffer Pointer to the packet buffer to send
 * @param packet_size Size of each packet in bytes
 * @param n Number of packets to send
 */
void send_n_packets(int conn_fd, char *buffer, int packet_size, int n);

/**
 * Returns the current time in seconds (as a double).
 * @return Current time in seconds
 */
double get_time_in_seconds(void);

/**
 * Waits to receive an ACK message from the server.
 * Exits if the receive fails or times out.
 * @param conn_fd Connected socket file descriptor
 */
void wait_for_ack(int conn_fd);

/**
 * Calculates the throughput based on the time interval and the total amount
 * of data sent in bytes.
 * @param start Start time in seconds
 * @param end End time in seconds
 * @return Throughput in MB/s
 */
double calc_throughput(double start, double end);

/*
 * Choice of number of packets to send:
 * the number of packets decreases as the packet size increases. This helps
 * reduce the risk of network congestion for large packets. Additionally,
 * to compare throughput fairly across different packet sizes,we send
 * the same total amount of data for each packet size and therefore, the
 * number of packets decreases as the packet size increases.
 */
/**
 * Runs the throughput measurement for a range of packet sizes (1 to
 * MAX_PACKET_SIZE). For each packet size, performs warmup cycles, sends
 * data, and prints throughput result.
 * @param conn_fd Connected socket file descriptor
 */
void measure_throughput_for_diff_packet_sizes(int conn_fd);


#endif //_CLIENT_H_
