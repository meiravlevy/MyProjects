#include "server.h"

int establish_server_socket(unsigned short port_num)
{
  int listen_fd;
  struct sockaddr_in server_addr;
  memset(&server_addr, 0, sizeof(server_addr)); //initialize the structure

  server_addr.sin_family = AF_INET; //using IPv4
  server_addr.sin_addr.s_addr = INADDR_ANY; //listen on all interfaces
  server_addr.sin_port = htons(port_num); //port to listen on

  //create socket
  listen_fd = create_socket();

  //bind
  if(bind(listen_fd, (struct sockaddr*) &server_addr, sizeof(server_addr)))
    cleanup_and_exit (listen_fd, -1, NULL, "bind");

  //listen for incoming connections
  if(listen(listen_fd, NUM_OF_CLIENTS) < 0)
    cleanup_and_exit (listen_fd, -1, NULL, "listen");
  return listen_fd;
}

void accept_conn_with_client(int *listen_fd_ptr, int *conn_fd_ptr) {
  *listen_fd_ptr = establish_server_socket(SERVER_PORT);
  //accept
  *conn_fd_ptr = accept(*listen_fd_ptr, NULL, NULL);
  if(*conn_fd_ptr < 0)
    cleanup_and_exit (*listen_fd_ptr, -1, NULL, "accept");
}

void recv_n_packets(int conn_fd, int listen_fd, char *recv_buffer, int
packet_size, int n) {
  for(int recv_packets = 0; recv_packets < n; recv_packets++) {
    // receive data from socket, wait for all requested bytes before continuing
    ssize_t res = recv (conn_fd, recv_buffer, packet_size, MSG_WAITALL);
    if(res <= 0) {
      cleanup_and_exit(conn_fd, listen_fd, recv_buffer, "receive");
    }
  }
}

void send_ack(int conn_fd, int listen_fd, char *recv_buffer) {
  ssize_t res = send(conn_fd, ACK_MSG, ACK_BYTES, 0);
  if(res != ACK_BYTES) {
    cleanup_and_exit(conn_fd, listen_fd, recv_buffer, "send ack");
  }
}

void recv_packets_for_diff_packet_sizes(int conn_fd, int listen_fd) {
  for(int packet_size = 1; packet_size <= MAX_PACKET_SIZE; packet_size *= 2) {
    int num_packets = DATA_TOTAL_BYTES / packet_size;

    //create buffer for receiving messages
    char *recv_buffer = create_buffer (conn_fd, listen_fd, packet_size);

    //read data
    int warmup_cycles = get_num_warmup_cycles (packet_size);
    int total_packets = num_packets + warmup_cycles;
    recv_n_packets (conn_fd, listen_fd, recv_buffer, packet_size,
                    total_packets);
    //send ack
    send_ack (conn_fd, listen_fd, recv_buffer);
    free(recv_buffer);
  }
}

int main (void)
{
  int conn_fd, listen_fd;
  accept_conn_with_client(&listen_fd, &conn_fd);
  recv_packets_for_diff_packet_sizes(conn_fd, listen_fd);
  close(conn_fd);
  close(listen_fd);
  return EXIT_SUCCESS;
}


