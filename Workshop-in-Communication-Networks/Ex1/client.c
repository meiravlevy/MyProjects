#include "client.h"

int establish_client_socket(const char *server_ip) {
  struct sockaddr_in server_addr;
  int conn_fd = create_socket();

  //set up server address
  memset(&server_addr, 0, sizeof(server_addr)); //initialize the structure
  server_addr.sin_family = AF_INET; //using IPv4
  server_addr.sin_port = htons(SERVER_PORT); // sets the port to connect to
  //convert string of server ip address to binary format and store it in server_addr.sin_addr
  if(inet_pton(AF_INET, server_ip, &server_addr.sin_addr) <= 0)
    cleanup_and_exit (conn_fd, -1, NULL, "inet pton");
  //connect client to server
  if(connect(conn_fd, (struct sockaddr *)&server_addr,
             sizeof(server_addr)) < 0)
    cleanup_and_exit (conn_fd, -1, NULL, "connect");
  return conn_fd;
}

void send_n_packets(int conn_fd, char *buffer, int packet_size, int n) {
  for(int i = 0; i < n; i++) {
    ssize_t res = send(conn_fd, buffer, packet_size, 0);
    if(res != packet_size) {
      cleanup_and_exit (conn_fd, -1, buffer, "send");
    }
  }
}

double get_time_in_seconds() {
  struct timeval tv;
  gettimeofday(&tv, NULL);
  return tv.tv_sec + tv.tv_usec / 1e6;
}

void wait_for_ack(int conn_fd) {
  char ack[ACK_BYTES];
  // read data from socket, wait for all requested bytes before continuing
  ssize_t res = recv (conn_fd, ack, sizeof(ack), MSG_WAITALL);
  if(res <= 0)
    cleanup_and_exit (conn_fd, -1, NULL, "receive ack");
}

double calc_throughput(double start, double end) {
  double time_period = end - start;
  double throughput = (DATA_TOTAL_BYTES / time_period)/(1024 * 1024);
  return throughput;
}

void measure_throughput_for_diff_packet_sizes(int conn_fd) {
  for(int packet_size = 1; packet_size <= MAX_PACKET_SIZE; packet_size *= 2) {
    int num_packets = DATA_TOTAL_BYTES / packet_size;

    char *send_buffer = create_buffer (conn_fd, -1, packet_size);
    memset(send_buffer, 1, packet_size); //initialize buffer

    //warm up cycles
    int warmup_cycles = get_num_warmup_cycles (packet_size);
    send_n_packets (conn_fd, send_buffer, packet_size, warmup_cycles);

    //measure throughput
    double start = get_time_in_seconds();
    send_n_packets (conn_fd, send_buffer, packet_size, num_packets);
    double end = get_time_in_seconds();
    free(send_buffer);
    wait_for_ack (conn_fd);
    double throughput = calc_throughput (start, end);
    printf("%d\t%.2f\tMB/s\n", packet_size, throughput);
  }
}


int main (int argc, char *argv[]) {
  if (argc != 2) {
    fprintf(stderr, "Usage: %s <server-ip>\n", argv[0]);
    exit(EXIT_FAILURE);
  }
  const char *server_ip = argv[1];
  int conn_fd = establish_client_socket (server_ip);
  measure_throughput_for_diff_packet_sizes(conn_fd);
  close(conn_fd);
  return EXIT_SUCCESS;
}