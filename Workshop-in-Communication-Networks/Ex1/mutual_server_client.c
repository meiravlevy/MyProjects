#include "mutual_server_client.h"

void cleanup_and_exit(int fd1, int fd2, char *buff, const char *msg) {
  if(buff != NULL) {
    free(buff);
  }
  if(fd1 >= 0) {
    close(fd1);
  }
  if(fd2 >= 0) {
    close(fd2);
  }
  perror(msg);
  exit(EXIT_FAILURE);
}

int create_socket() {
  int fd = socket(AF_INET, SOCK_STREAM, 0);
  if(fd < 0)
  {
    perror("socket");
    exit(EXIT_FAILURE);
  }
  return fd;
}

char *create_buffer(int fd1, int fd2, int packet_size) {
  char *buffer = malloc(packet_size);
  if(!buffer)
    cleanup_and_exit (fd1, fd2, NULL, "malloc");
  return buffer;
}

int get_num_warmup_cycles(int packet_size){
  if (packet_size <= 128)
    return 1000;
  if (packet_size <= 8192)
    return 500;
  return 100;
}