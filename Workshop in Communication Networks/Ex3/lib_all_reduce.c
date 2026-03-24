#include "lib_all_reduce.h"


// ======================== Small Utilities ===================

// Tiny logging helper
static void log_perror(const char *msg) {
  int e = errno;
  fprintf(stderr, "Error: %s: %s\n", msg, strerror(e));
}


// ================== Hostname and rank helpers =================

/**
 * @brief Free an array of heap-allocated strings.
 *
 * Frees each hosts[i] for i in [0, n) and then frees the hosts array itself.
 * Safe to call with hosts == NULL (no-op).
 *
 * @param hosts  Array of C-string pointers (may be NULL).
 * @param n      Number of elements in the hosts array.
 */
static void free_hosts(char **hosts, int n) {
  if (!hosts) return;
  for (int i = 0; i < n; ++i){
    free(hosts[i]);
    hosts[i] = NULL;
  }
  free(hosts);
  hosts = NULL;
}

/**
 * @brief Parses a string of server names into a dynamically allocated array.
 *
 * @param input A non-NULL string containing at least two server names separated by
 *              space, tab, or newline characters. (e.g. "srv1 srv2 ...").
 * @param out_hosts Output pointer to an allocated array of malloc’d strings.
 * @param out_count Output pointer to the number of servers found.
 *
 * @return 0 on Success, -1 on Invalid arguments, allocation failure, or
 * less than 2 servers
 */

static int parse_server_list(const char *input, char ***out_hosts, int *out_count) {

  // Tokenize a working copy (strtok_r modifies the buffer)
  char *buf = strdup(input);
  if (!buf) return -1;

  /* Start with capacity 8 as a small power-of-two default to
   * reduce reallocations without wasting memory. */
  int capacity = 8;
  int count = 0;
  char **hosts = (char **)malloc(sizeof(char*) * (size_t)capacity);
  if (!hosts) { free(buf); return -1; }

  char *save = NULL;
  /*
   * explanation of for loop conditions:
   * start tokenizing at the start of buf. keep looping while a token exists.
   * get next token using saved state.
   */
  for (char *tok = strtok_r(buf, " \t\r\n", &save);
       tok != NULL;
       tok = strtok_r(NULL, " \t\r\n", &save)) {

    if (count == capacity) { //if the array is full, double the capacity
      int new_cap = capacity * 2;
      char **tmp = (char **)realloc(hosts, sizeof(char*) * (size_t)new_cap);
      if (!tmp) {
        free_hosts(hosts, count);
        hosts = NULL;
        free(buf);
        return -1;
      }
      hosts = tmp;
      capacity = new_cap;
    }

    hosts[count] = strdup(tok); //allocates a fresh copy of the token.
    if (!hosts[count]) {
      free_hosts(hosts, count);
      hosts = NULL;
      free(buf);
      return -1;
    }
    count++;
  }

  free(buf);

  if (count < 2) { // ring needs at least 2
    free_hosts(hosts, count);
    hosts = NULL;
    fprintf(stderr, "Error: need at least 2 servers, got %d\n", count);
    return -1;
  }

  *out_hosts = hosts;
  *out_count = count;
  return 0;
}

/**
 * @brief Retrieve the local host name without its domain suffix.
 *
 * Gets the system hostname, removes any domain part after the first dot,
 * and stores the short name in the provided buffer.
 *
 * @param out  Character array of size NI_MAXHOST to receive the short hostname.
 *             The string is always null-terminated.
 *
 * @return 0 on success, -1 on failure
 */

static int get_self_short_hostname(char out[NI_MAXHOST]) {
  char sys[HOST_NAME_MAX + 1];
  if (gethostname(sys, sizeof(sys)) != 0) { log_perror("gethostname"); return -1; }
  sys[HOST_NAME_MAX] = '\0';

  // Strip domain (e.g., "node01.cs.example.edu" → "node01")
  char *dot = strchr(sys, '.'); //looks for the first dot and truncates at the dot
  if (dot) *dot = '\0';

  // Copy to caller buffer
  strncpy(out, sys, NI_MAXHOST - 1);
  out[NI_MAXHOST - 1] = '\0';
  return 0;
}

/**
 * @brief Find this machine’s rank in the host list by exact name match.
 *
 * @param hosts      Array of host name strings.
 * @param n          Number of elements in the hosts array.
 * @param self_short Short hostname of the current machine (no domain).
 *
 * @return
 *         Rank (0-based index) if found,
 *        -1 if no exact match is found.
 */
static int find_rank_in_hosts(char **hosts, int n, const char *self_short) {
  for (int i = 0; i < n; ++i)
    if (strcmp(self_short, hosts[i]) == 0)
      return i;
  return -1;
}

// ================== TCP connection ==========================

/**
 * resolve_host - Resolve a hostname or IPv4 string into a sockaddr_in.
 *
 * @host: Hostname or IPv4 string (e.g. "example.com" or "192.0.2.10").
 * @port: TCP port number to use.
 * @out:  Output pointer where the resolved IPv4 address/port will be stored.
 *
 * Returns 0 on success, -1 on failure.
 */
static int resolve_host(const char *host, uint16_t port, struct sockaddr_in *out) {
  struct addrinfo hints = {0}, *res = NULL;

  // Request IPv4 (AF_INET) and TCP (SOCK_STREAM) results
  hints.ai_family   = AF_INET;
  hints.ai_socktype = SOCK_STREAM;

  // Resolve hostname -> addrinfo list
  int rc = getaddrinfo(host, NULL, &hints, &res);
  if (rc != 0) {
    fprintf(stderr, "Error: getaddrinfo('%s'): %s\n", host, gai_strerror(rc));
    return -1;
  }

  // Build IPv4 socket address
  struct sockaddr_in addr = {0};
  addr.sin_family = AF_INET;
  addr.sin_port   = htons(port);  // store port in network byte order
  addr.sin_addr   = ((struct sockaddr_in *)res->ai_addr)->sin_addr; // copy IPv4 address

  freeaddrinfo(res); // release resolver’s memory

  *out = addr;       // copy struct by value into caller’s buffer
  return 0;
}

/**
 * set_nonblocking - Put a file descriptor into non-blocking mode.
 *
 * @fd: File descriptor (e.g. a socket).
 *
 * Returns 0 on success, -1 on failure.
 *
 * In non-blocking mode, operations like connect, accept, recv, send
 * return immediately instead of waiting. If the operation would block,
 * they fail with errno = EAGAIN / EWOULDBLOCK (or EINPROGRESS for connect).
 */
static int set_nonblocking(int fd) {
  // Get current file status flags (like O_APPEND, O_NONBLOCK, etc.)
  int flags = fcntl(fd, F_GETFL, 0);
  if (flags < 0) {
    log_perror("fcntl(F_GETFL)");
    return -1;
  }

  // Set the O_NONBLOCK flag in addition to existing flags
  if (fcntl(fd, F_SETFL, flags | O_NONBLOCK) < 0) {
    log_perror("fcntl(F_SETFL)");
    return -1;
  }

  return 0;
}


/**
 * @brief Create a TCP listening socket on the given port.
 *
 * This helper encapsulates the common steps required to start a
 * server socket: it creates an IPv4 stream socket, enables the
 * SO_REUSEADDR option so the address can be rebound quickly after a
 * restart, binds the socket to all local interfaces on the specified
 * port, and finally calls listen() to prepare it to accept incoming
 * connections.
 *
 * @param port  The TCP port number (in host byte order) to listen on.
 * @return      A non‑negative file descriptor on success, or -1 on
 *              error.
 */
static int create_listen_socket(uint16_t port) {
  /* Create an IPv4/TCP socket */
  int fd = socket(AF_INET, SOCK_STREAM, 0);
  if (fd < 0) {
    log_perror("socket");
    return -1;
  }
  /* Allow the port to be reused immediately after the process exits */
  int opt = 1;
  if (setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) < 0) {
    log_perror("setsockopt(SO_REUSEADDR)");
    close(fd);
    return -1;
  }
  /* Prepare the local address structure */
  struct sockaddr_in addr;
  memset(&addr, 0, sizeof(addr));
  addr.sin_family = AF_INET;
  addr.sin_addr.s_addr = htonl(INADDR_ANY); /* listen on all interfaces */
  addr.sin_port = htons(port);
  /* Bind the socket to the local address */
  if (bind(fd, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
    log_perror("bind");
    close(fd);
    return -1;
  }
  /* Mark the socket as passive (ready to accept connections) */
  if (listen(fd, 1) < 0) {
    log_perror("listen");
    close(fd);
    return -1;
  }
  return fd;
}

/**
 * Check if a non-blocking connect() has completed.
 *
 * @param fd  Socket file descriptor.
 * @return 1 if connected successfully, -1 on error (errno is set).
 * */
static int check_connect_complete(int fd) {
  int err = 0;
  socklen_t len = sizeof(err);
  // Ask kernel for pending socket error (connect result)
  if (getsockopt(fd, SOL_SOCKET, SO_ERROR, &err, &len) < 0) {
    log_perror("getsockopt");
    return -1;
  }
  if (err == 0)
    return 1; /* success */
  errno = err;
  return -1;    /* failure */
}

// ======================= RDMA helpers =======================

/**
 * Transition an RC Queue Pair from RESET -> INIT.
 *
 * Binds the QP to a given HCA port, sets partition (P_Key) index,
 * and programs which remote/local accesses are allowed.
 *
 * @param qp        The QP to modify (must currently be in RESET).
 * @param port_num  HCA port number (usually 1 in lab setups).
 * @return 0 on success, nonzero on failure (errno may be set by provider).
 */
static int qp_to_init(struct ibv_qp *qp, uint8_t port_num) {
  struct ibv_qp_attr attr = {0};                // zero-initialize attributes

  attr.qp_state        = IBV_QPS_INIT;          // target state
  attr.pkey_index      = 0;                     // default P_Key partition
  attr.port_num        = port_num;              // bind QP to HCA port
  attr.qp_access_flags =                        // what remote ops we allow:
      IBV_ACCESS_REMOTE_WRITE |               //  - peer may RDMA WRITE into us
      IBV_ACCESS_REMOTE_READ  |               //  - peer may RDMA READ from us
      IBV_ACCESS_LOCAL_WRITE;                 //  - we may WRITE locally (for RECV buffers, etc.)

  // Tell ibv_modify_qp which fields in 'attr' are valid for this transition
  int mask = IBV_QP_STATE | IBV_QP_PKEY_INDEX | IBV_QP_PORT |
             IBV_QP_ACCESS_FLAGS;

  // Apply the change: RESET -> INIT
  return ibv_modify_qp(qp, &attr, mask);
}

/**
 * Convert a binary 16-byte GID into a 32-character hex string.
 *
 * Each 4-byte chunk of the GID is printed as 8 hex digits
 * (after converting to network byte order), producing a
 * consistent 32-char lowercase hex representation.
 *
 * @param gid        Pointer to union ibv_gid (16 raw bytes).
 * @param wire_gid Output buffer; must have space for 33 bytes
 *                   (32 hex chars + terminating '\0').
 */
void gid_to_wire_gid(const union ibv_gid *gid, char wire_gid[])
{
  for (int i = 0; i < 4; ++i)
    sprintf(&wire_gid[i * 8], "%08x", htonl(*(uint32_t *)(gid->raw + i * 4)));
}

/**
 * Serialize an RDMA endpoint into a fixed-width wire string.
 *
 * Format: "LLLL:QQQQQQ:PPPPPP:GG..GG"
 *   - LID: 4 hex digits (zero-padded)
 *   - QPN: 6 hex digits
 *   - PSN: 6 hex digits
 *   - GID: 32 hex digits
 *
 * @param ep   Pointer to endpoint structure to serialize.
 * @param out Output buffer (must be at least WIRE_STR_LEN bytes).
 */
static void ep_to_wire(const struct rdma_ep *ep, char out[WIRE_STR_LEN]) {
  char gid[33]; // temporary buffer to hold the 32-char hex GID plus '\0'
  gid_to_wire_gid(&ep->gid, gid); // fills gid with 32-hex representation.
  snprintf(out, WIRE_STR_LEN, "%04x:%06x:%06x:%s",
           ep->lid, ep->qpn, ep->psn, gid);
}


/**
 * Convert a 32-character hex string back into a binary ibv_gid.
 *
 * The input string (wire_gid) is expected to be the output of
 * gid_to_wire_gid(), i.e. 32 lowercase hex digits representing a 16-byte GID.
 * The function parses 8 hex chars at a time into a 32-bit value,
 * converts from network to host byte order, and writes into gid->raw.
 *
 * @param wire_gid Input GID string (32 hex chars + '\0').
 * @param gid  Output pointer to union ibv_gid (16-byte binary form).
 */
void wire_gid_to_gid(const char *wire_gid, union ibv_gid *gid)
{
  char tmp[9]; // temp buffer for 8 hex chars + null terminator
  uint32_t v32;
  int i;

  for (tmp[8] = 0, i = 0; i < 4; ++i) {
    memcpy(tmp, wire_gid + i * 8, 8); // copy next 8 hex characters from wire string
    sscanf(tmp, "%x", &v32); // convert that 8-char hex substring to 32-bit integer
    *(uint32_t *)(&gid->raw[i * 4]) = ntohl(v32);
  }
}

/**
 * Parse a wire-format endpoint string into an rdma_ep struct.
 *
 * Expected format: "LLLL:QQQQQQ:PPPPPP:GG..GG"
 *   - LID: 4 hex digits (16-bit)
 *   - QPN: 6 hex digits
 *   - PSN: 6 hex digits
 *   - GID: 32 hex digits (as a string)
 *
 * Uses sscanf() to parse LID, QPN, and PSN, then converts the GID
 * string back into a binary union ibv_gid with wire_gid_to_gid().
 *
 * @param in Input string (WIRE_STR_LEN characters).
 * @param e  Output pointer to rdma_ep structure to fill.
 * @return 0 on success, -1 on parse error.
 */
static int wire_to_ep(const char in[WIRE_STR_LEN], struct rdma_ep *ep) {
  char gid[33] = {0};
  if (sscanf(in, "%hx:%x:%x:%32s", &ep->lid, &ep->qpn, &ep->psn, gid) != 4)
    // fail if not all 4 fields parsed
    return -1;
  wire_gid_to_gid(gid, &ep->gid); // convert hex GID string back to binary form
  return 0;
}

/**
 * Send an entire buffer reliably over a socket.
 *
 * Keeps calling send() until all len bytes from buf are written,
 * handling short writes and EINTR interruptions.
 *
 * @param fd   Socket file descriptor to send on.
 * @param buf  Pointer to data buffer.
 * @param len  Number of bytes to send.
 * @return 0 on success (all bytes sent), -1 on error.
 */
static int send_all(int fd, const void *buf, size_t len) {
  const uint8_t *cur_loc_in_buf = (const uint8_t*)buf;
  while (len) { // loop until all bytes sent
    ssize_t n = send(fd, cur_loc_in_buf, len, 0); // attempt to send remaining bytes
    if (n < 0) { // if send failed
      if (errno == EINTR) continue;
      return -1;
    }
    cur_loc_in_buf += (size_t)n; // increase pointer by bytes sent
    len -= (size_t)n;
  }
  return 0;
}

/**
 * Receive exactly len bytes from a socket into buf.
 *
 * Repeatedly calls recv() until the buffer is full, handling
 * partial reads and EINTR interruptions. Uses MSG_WAITALL to
 * request that the kernel block until the requested number of
 * bytes are available, but still loops for safety.
 *
 * @param fd   Socket file descriptor to read from.
 * @param buf  Destination buffer.
 * @param len  Number of bytes to read.
 * @return 0 on success (all bytes received), -1 on error or EOF.
 */

static int recv_all(int fd, void *buf, size_t len) {
  uint8_t *cur_loc_in_buf = (uint8_t*)buf;
  while(len) {
    ssize_t n = recv(fd, cur_loc_in_buf, len, MSG_WAITALL);
    if (n <= 0) {
      if (n < 0 && errno == EINTR) continue; // retry if interrupted
      return -1; // error or EOF
    }
    cur_loc_in_buf += (size_t)n;
    len -= (size_t)n;
  }
  return 0;
}

/**
 * Transition an RC (Reliable Connection) QP into the Ready-to-Send state
 * using the provided remote endpoint information.
 *
 * This function sets the QP to RTR (Ready-to-Receive), filling in details
 * about the remote peer (QPN, PSN, LID/GID, path MTU, etc.), and then
 * transitions it to RTS (Ready-to-Send) with appropriate retry/timeout
 * parameters.
 *
 * @param qp       Queue Pair to modify.
 * @param ib_port  Local IB port number used for this connection.
 * @param my_psn   Local Packet Sequence Number (start value).
 * @param mtu      Maximum Transmission Unit (IBV_MTU_256, _512, _1024, etc).
 * @param sl       Service Level (QoS field, typically 0).
 * @param remote_ep      Pointer to remote endpoint info (LID, QPN, PSN, GID).
 * @param sgid_idx Source GID index (used if GIDs are exchanged, e.g. RoCE).
 * @return 0 on success, -1 on failure.
 */
static int qp_connect_rc(struct ibv_qp *qp,
                         int ib_port,
                         uint32_t my_psn,
                         enum ibv_mtu mtu,
                         int sl,
                         const struct rdma_ep *remote_ep,
                         int sgid_idx, struct ibv_device_attr* dev_attr,
                         struct pg_handle* pg)
{
  struct ibv_qp_attr qp_attr;
  int flags;

  // --- Move QP to RTR (Ready to Receive) ---
  memset(&qp_attr, 0, sizeof(qp_attr));
  qp_attr.qp_state           = IBV_QPS_RTR;
  qp_attr.path_mtu           = mtu; //how big each packet can be
  qp_attr.dest_qp_num        = remote_ep->qpn;   // which remote QPN to talk to
  qp_attr.rq_psn             = remote_ep->psn;   // remote starting PSN
  // Allow us to issue multiple RDMA READs concurrently (for rendezvous pipeline)
  uint32_t peer_read_window = (dev_attr->max_qp_rd_atom >= 8) ? 8 :
                              dev_attr->max_qp_rd_atom;
  qp_attr.max_dest_rd_atomic = peer_read_window; // outstanding RDMA reads
  pg->max_pipe_depth = qp_attr.max_dest_rd_atomic;
  qp_attr.min_rnr_timer      = QP_ATTR_MIN_RNR;         // RNR NAK timer

  qp_attr.ah_attr.is_global  = (remote_ep->gid.global.interface_id != 0ULL ||
                                remote_ep->gid.global.subnet_prefix != 0ULL); //decides if to use gid or lid
  qp_attr.ah_attr.dlid       = remote_ep->lid;   // remote LID (for IB)
  qp_attr.ah_attr.sl         = sl;         // service level
  qp_attr.ah_attr.src_path_bits = 0;
  qp_attr.ah_attr.port_num   = ib_port;  // which local port to send from

  if (qp_attr.ah_attr.is_global) {
    qp_attr.ah_attr.grh.dgid       = remote_ep->gid;  // remote GID
    qp_attr.ah_attr.grh.sgid_index = sgid_idx;  // local SGID index
    qp_attr.ah_attr.grh.hop_limit  = 1;         // no routing hops
  }

  flags = IBV_QP_STATE              |
          IBV_QP_AV                 |
          IBV_QP_PATH_MTU           |
          IBV_QP_DEST_QPN           |
          IBV_QP_RQ_PSN             |
          IBV_QP_MAX_DEST_RD_ATOMIC |
          IBV_QP_MIN_RNR_TIMER;

  if (ibv_modify_qp(qp, &qp_attr, flags)) {
    perror("ibv_modify_qp to RTR");
    return -1;
  }

  // --- Move QP to RTS (Ready to Send) ---
  memset(&qp_attr, 0, sizeof(qp_attr));
  qp_attr.qp_state      = IBV_QPS_RTS;
  qp_attr.timeout       = QP_ATTR_TIMEOUT;  // local ACK timeout (~ 4s)
  qp_attr.retry_cnt     = QP_ATTR_RETRY_CNT;   // retry infinite times
  qp_attr.rnr_retry     = QP_ATTR_RNR_RETRY;   // RNR NAK retry infinite times
  qp_attr.sq_psn        = my_psn; // our starting PSN
  uint32_t my_read_window = (dev_attr->max_qp_rd_atom >= 8) ? 8 :
                            dev_attr->max_qp_rd_atom;
  qp_attr.max_rd_atomic = my_read_window;   // allow us to issue multiple concurrent RDMA READs

  flags = IBV_QP_STATE        |
          IBV_QP_TIMEOUT      |
          IBV_QP_RETRY_CNT    |
          IBV_QP_RNR_RETRY    |
          IBV_QP_SQ_PSN       |
          IBV_QP_MAX_QP_RD_ATOMIC;

  if (ibv_modify_qp(qp, &qp_attr, flags)) {
    perror("ibv_modify_qp to RTS");
    return -1;
  }
  return 0;
}


// ======================== Public API ========================
int connect_process_group(const char *server_list, void **pg_handle_out)
{
  if (!server_list || !pg_handle_out) return -1;

  // Parse the server list (space-separated)
  char **hosts = NULL;
  int n_hosts = 0;
  if (parse_server_list (server_list, &hosts, &n_hosts) != 0)
  {
    fprintf (stderr, "Error: failed to parse server list\n");
    return -1;
  }

  // Determine my short hostname and rank in the list
  char self_short[NI_MAXHOST];
  if (get_self_short_hostname (self_short) != 0)
  {
    free_hosts (hosts, n_hosts);
    hosts = NULL;
    return -1;
  }

  // The next lines are if servers 3,4 are not working.
  int rank;
  // If FORCE_RANK is set, use it; otherwise fall back to hostname matching.
  char *rank_env = getenv ("FORCE_RANK");
  if (rank_env)
  {
    char *endptr = NULL;
    long val = strtol (rank_env, &endptr, 10);
    if (*endptr != '\0')
    {
      fprintf (stderr, "Error: FORCE_RANK='%s' is not a valid number\n", rank_env);
      free_hosts (hosts, n_hosts);
      return -1;
    }
    rank = (int) val;
    if (rank < 0 || rank >= n_hosts)
    {
      fprintf (stderr, "Error: FORCE_RANK=%d is out of range [0..%d]\n",
               rank, n_hosts - 1);
      free_hosts (hosts, n_hosts);
      return -1;
    }
  }
  else
  {
    rank = find_rank_in_hosts (hosts, n_hosts, self_short);
    if (rank < 0)
    {
      fprintf (stderr,
               "Error: my hostname '%s' not found in server list\n",
               self_short);
      free_hosts (hosts, n_hosts);
      hosts = NULL;
      return -1;
    }
  }

//next comments below are if all the servers(1-4) are working
//  int rank = find_rank_in_hosts(hosts, n_hosts, self_short);

//  if (rank < 0) {
//    fprintf(stderr, "Error: my hostname '%s' not found in server list\n", self_short);
//    free_hosts(hosts, n_hosts);
//    hosts = NULL;
//    return -1;
//  }

  int right_rank = (rank + 1) % n_hosts;


  // Bring up the ring: listen for LEFT, connect to RIGHT
  uint16_t listen_port = BASE_PORT + rank;
  uint16_t connect_port = BASE_PORT + right_rank;


  int right_fd = -1, left_fd = -1;
  /* create listening socket */
  int listen_fd = create_listen_socket(listen_port);
  if (listen_fd < 0) {
    free_hosts(hosts, n_hosts);
    return -1;
  }

  /* resolve right neighbour */
  struct sockaddr_in right_addr; // will hold the ipv4 addr + port of right neighbor
  if (resolve_host(hosts[right_rank], connect_port, &right_addr) != 0) {
    close(listen_fd);
    free_hosts(hosts, n_hosts);
    return -1;
  }

  /* attempt non-blocking connect to the right neighbour */
  int is_connected;
  while (1) {
    right_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (right_fd < 0) {
      log_perror("socket");
      goto fail;
    }
    if (set_nonblocking(right_fd) < 0)
      goto fail;

    is_connected = connect(right_fd, (struct sockaddr *)&right_addr,
                           sizeof(right_addr));
    if (is_connected == 0 || errno == EINPROGRESS)
      // success now, or handshake in progress
      break;

    // Real failure: close and retry
    log_perror("connect");
    close(right_fd);
    right_fd = -1;
  }

  int have_left = 0;
  int have_right = (is_connected == 0);

  while (!have_left || !have_right) {
    struct pollfd pfds[2];

    pfds[0].fd     = listen_fd;
    pfds[0].events = POLLIN; //notify when incoming connection is ready to be accepted

    pfds[1].fd     = right_fd;
    pfds[1].events = POLLOUT; //notify when the non-blocking connect is complete

    // blocks until one or more events are ready. (writes to .revents)
    int rc = poll(pfds, 2, -1);
    if (rc < 0) {
      log_perror("poll");
      goto fail;
    }

    // --- Handle LEFT (accept connection) ---
    if (!have_left && (pfds[0].revents & POLLIN)) {
      left_fd = accept(listen_fd, NULL, NULL);
      if (left_fd < 0) {
        //EAGAIN and EWOULDBLOCK are not fatal errors so we can retry later.
        if (errno != EAGAIN && errno != EWOULDBLOCK) {
          log_perror("accept");
          goto fail;
        }
        // Otherwise: no connection ready — try again later
      } else {
        have_left = 1;
      }
    }

    // --- Handle RIGHT (complete non-blocking connect) ---
    /* If we haven’t connected yet, and the socket is ready for writing
     * (POLLOUT) or error events (POLLERR, POLLHUP) occurred, we must check
     * what happened.
     */
    if (!have_right && (pfds[1].revents & (POLLOUT | POLLERR | POLLHUP))) {
      int is_connection_complete = check_connect_complete(right_fd);
      if (is_connection_complete == 1) { //success
        // Connected: switch to blocking mode
        int flags = fcntl(right_fd, F_GETFL, 0);
        if (flags >= 0)
          fcntl(right_fd, F_SETFL, flags & ~O_NONBLOCK);
        have_right = 1;
      } else {
        // Connect failed: retry
        close(right_fd);
        right_fd = socket(AF_INET, SOCK_STREAM, 0);
        if (right_fd >= 0 && set_nonblocking(right_fd) == 0) {
          is_connected = connect(right_fd, (struct sockaddr *)&right_addr, sizeof(right_addr));
          if (is_connected == 0) { //if connection succeeded
            have_right = 1;
          } else if (is_connected < 0 && errno != EINPROGRESS) {
            close(right_fd);
            right_fd = -1;
          }
        }
      }
    }
  }

  /* clean up listen socket */
  close(listen_fd);
  listen_fd = -1;


  pg_handle *pg = calloc(1, sizeof(struct pg_handle));
  if (!pg) {
    perror("calloc");
    goto fail; }

  pg->left_fd  = left_fd;
  pg->right_fd = right_fd;
  pg->rank     = rank;
  pg->nprocs   = n_hosts;
  pg->ib_port  = 1;       // lab default

  // Open device, PD, CQ (same pattern as your template)
  int num_devices = 0; //number of rdma devices found on the system
  // Query system for available RDMA devices (HCAs).
  struct ibv_device **devices = ibv_get_device_list(&num_devices);
  if (!devices || num_devices == 0) {
    fprintf(stderr,"No IB device\n"); goto fail; }
  // Open the first RDMA device in the list -> get a context handle
  pg->ctx = ibv_open_device(devices[0]);
  ibv_free_device_list(devices);
  if (!pg->ctx) { perror("ibv_open_device"); goto fail; }

  pg->pd = ibv_alloc_pd(pg->ctx); //allocates a pd on this device
  if (!pg->pd) { perror("ibv_alloc_pd"); goto fail; }

  // Create a Completion Queue (CQ)
  //   - h->ctx: which device context to use
  //   - 512: max number of completion entries (CQEs)
  //   - NULL: cq_context (unused here)
  //   - NULL: completion channel (NULL = we’ll poll manually)
  //   - 0: completion vector (ignored since no channel)
  // CQ collects notifications of finished send/recv/RDMA operations.
  pg->cq = ibv_create_cq(pg->ctx, 512, NULL, NULL, 0);
  if (!pg->cq) { perror("ibv_create_cq"); goto fail; }

  // Create two RC QPs to neighbors (share same CQ)

  // Query device capabilities
  struct ibv_device_attr dev_attr;
  if (ibv_query_device(pg->ctx, &dev_attr) != 0) {
    perror("ibv_query_device");
    goto fail;
  }

  // Pick values, capped at 128
  const uint32_t send_wr = (dev_attr.max_qp_wr >= 128) ? 128 : dev_attr
      .max_qp_wr;
  const uint32_t recv_wr = (dev_attr.max_qp_wr >= 128) ? 128 : dev_attr
      .max_qp_wr;
  const uint32_t max_sge = 1;   // contiguous chunks only

  struct ibv_qp_init_attr qp_init_attr = {
      .send_cq = pg->cq,
      .recv_cq = pg->cq,
      .cap = {
          .max_send_wr     = send_wr,
          .max_recv_wr     = recv_wr,
          .max_send_sge    = max_sge,
          .max_recv_sge    = max_sge,
      },
      .qp_type = IBV_QPT_RC
  };

  pg->qp_left  = ibv_create_qp(pg->pd, &qp_init_attr);
  pg->qp_right = ibv_create_qp(pg->pd, &qp_init_attr);
  if (!pg->qp_left || !pg->qp_right) {
    fprintf(stderr,"create_qp failed\n"); goto fail; }

  if (qp_to_init(pg->qp_left,  pg->ib_port) ||
      qp_to_init(pg->qp_right, pg->ib_port)) {
    fprintf(stderr,"QP INIT failed\n"); goto fail;
  }

  // Query local LID/GID (same as before)
  struct ibv_port_attr port_attr = {0};
  if (ibv_query_port(pg->ctx, pg->ib_port, &port_attr)) {
    perror("ibv_query_port");
    goto fail;
  }
  pg->local_left.lid  = port_attr.lid;
  pg->local_right.lid = port_attr.lid;
  int gid_idx = 0;
  // Query the Global Identifier (GID) at index `gid_idx` for this port.
  // success - 0. failure - non-zero
  if (ibv_query_gid(pg->ctx, pg->ib_port, gid_idx,
                    &pg->local_left.gid))
    //if failure - set the gid field to 0
    memset(&pg->local_left.gid, 0, sizeof(pg->local_left.gid));
  if (ibv_query_gid(pg->ctx, pg->ib_port, gid_idx,
                    &pg->local_right.gid))
    memset(&pg->local_right.gid, 0, sizeof(pg->local_right.gid));

  // Assign QPNs and PSNs
  // Save QP numbers assigned by the device
  pg->local_left.qpn  = pg->qp_left->qp_num;
  pg->local_right.qpn = pg->qp_right->qp_num;

  // Seed the random number generator using current time XOR rank
  // Ensures each process/rank gets a different random sequence
  srand((unsigned)(time(NULL) ^ (rank<<8)));

  // Choose random 24-bit initial PSNs for each QP
  // (PSN = Packet Sequence Number, must be in [0 .. 0xFFFFFF])
  pg->local_left.psn  = rand() & 0xFFFFFF;
  pg->local_right.psn = rand() & 0xFFFFFF;

  // Exchange endpoints over the already-built ring TCP
  // Send to the side you connect to; receive from the side that accepts.
  char msg_out[WIRE_STR_LEN], msg_in[WIRE_STR_LEN];

// (a) Tell RIGHT about the QP you’ll use to talk to RIGHT
  ep_to_wire(&pg->local_right, msg_out);
  if (send_all(pg->right_fd, msg_out, sizeof(msg_out)) != 0) {
    perror("send_all right");
    goto fail;
  }

// (b) Receive LEFT’s QP for talking to you
  if (recv_all(pg->left_fd, msg_in, sizeof(msg_in)) != 0) {
    perror("recv_all left");
    goto fail;
  }
  if (wire_to_ep(msg_in, &pg->remote_left) != 0) {
    fprintf(stderr,"parse left ep failed\n");
    goto fail;
  }

  // Symmetric: tell LEFT about the QP you’ll use to talk LEFT; get RIGHT’s ep
  ep_to_wire(&pg->local_left, msg_out);
  if (send_all(pg->left_fd, msg_out, sizeof(msg_out)) != 0) {
    perror("send_all left");
    goto fail;
  }
  if (recv_all(pg->right_fd, msg_in, sizeof(msg_in)) != 0) {
    perror("recv_all right");
    goto fail;
  }
  if (wire_to_ep(msg_in, &pg->remote_right) != 0) {
    fprintf(stderr,"parse right ep failed\n");
    goto fail;
  }

  // Bring both QPs to RTR/RTS
  enum ibv_mtu mtu = port_attr.active_mtu;  // or from arg, like your template
  int sl = 0;                       // service level (same as template)
  if (qp_connect_rc(pg->qp_left,  pg->ib_port,
                    pg->local_left.psn, mtu, sl,
                    &pg->remote_left, gid_idx, &dev_attr, pg))  {
    fprintf(stderr, "connect left failed\n");
    goto fail;
  }
  if (qp_connect_rc(pg->qp_right, pg->ib_port,
                    pg->local_right.psn, mtu, sl,
                    &pg->remote_right, gid_idx, &dev_attr, pg))  {
    fprintf(stderr,"connect right failed\n");
    goto fail;
  }

  // Hand out the handle
  *pg_handle_out = pg;

  // Close the tcp connection
  if (left_fd >= 0){
    close(left_fd);
    left_fd = -1;
  }
  if (right_fd >= 0){
    close(right_fd);
    right_fd = -1;
  }
  if(hosts) {
    free_hosts(hosts, n_hosts);
    hosts = NULL;
  }
  // --- Staging buffer where RDMA READ results land (one slot per inflight chunk) ---
  pg->total_staging_bytes = MAX_CHUNK_BYTES * pg->max_pipe_depth;
  if (!pg->base_staging_recv) {
    if (posix_memalign((void **)&pg->base_staging_recv, 4096,
                       pg->total_staging_bytes) != 0)
      goto fail;
    // The destination of an RDMA READ must allow LOCAL_WRITE (the local RNIC writes into it).
    pg->staging_mr = ibv_reg_mr(pg->pd, pg->base_staging_recv,
                                pg->total_staging_bytes,
                                IBV_ACCESS_LOCAL_WRITE);
    if (!pg->staging_mr){
      perror("ibv_reg_mr(staging)");
      goto fail;
    }
  }


  if (!pg->base_ctrl_send || !pg->base_ctrl_recv) {
    // Allocate page-aligned memory for ctrl_send and ctrl_recv
    if (posix_memalign((void **)&pg->base_ctrl_send, 4096,
                       sizeof(struct ctrl_hdr)) != 0)
      goto fail;

    if (posix_memalign((void **)&pg->base_ctrl_recv, 4096,
                       sizeof(struct ctrl_hdr)) != 0)
      goto fail;
    /*zero both control buffers to avoid garbage bits going on the wire or
    being read */
    memset(pg->base_ctrl_send, 0, sizeof(struct ctrl_hdr));
    memset(pg->base_ctrl_recv, 0, sizeof(struct ctrl_hdr));

    pg->ctrl_send_mr = ibv_reg_mr(pg->pd, pg->base_ctrl_send,
                                  sizeof(struct ctrl_hdr),
                                  IBV_ACCESS_LOCAL_WRITE |
                                  IBV_ACCESS_REMOTE_READ);
    pg->ctrl_recv_mr = ibv_reg_mr(pg->pd, pg->base_ctrl_recv,
                                  sizeof(struct ctrl_hdr),
                                  IBV_ACCESS_LOCAL_WRITE|
                                  IBV_ACCESS_REMOTE_READ);
    // if either registration failed, return -1
    if (!pg->ctrl_send_mr || !pg->ctrl_recv_mr){
      perror("ibv_reg_mr(ctrl_hdr)");
      goto fail;
    }
  }

  // --- ack buffers (eager acks) ---
  if (!pg->ack_send_buf) {
    if (posix_memalign((void**)&pg->ack_send_buf, 64, 1) != 0) goto fail;
    if (posix_memalign((void**)&pg->ack_recv_buf, 64, 1) != 0) goto fail;

    pg->ack_send_mr = ibv_reg_mr(pg->pd, pg->ack_send_buf, 1, IBV_ACCESS_LOCAL_WRITE);
    pg->ack_recv_mr = ibv_reg_mr(pg->pd, pg->ack_recv_buf, 1, IBV_ACCESS_LOCAL_WRITE);
    if (!pg->ack_send_mr || !pg->ack_recv_mr) {
      perror("ibv_reg_mr(ack)"); goto fail;
    }
  }
  return 0;

  fail:
  if (listen_fd >= 0) close(listen_fd);
  if (hosts) free_hosts(hosts, n_hosts);
  return -1;
}



// ================== Reduce-Scatter (ring) ==================

/**
 * @brief Get the size in bytes of a given datatype.
 *
 * Maps a DATATYPE enum value (e.g., DT_INT32, DT_FLOAT32, DT_FLOAT64)
 * to its corresponding element size in bytes.
 *
 * @param dt  The datatype identifier.
 * @return    Size of one element in bytes, or 0 if unsupported.
 */
static size_t dt_size(DATATYPE dt) {
  switch (dt) {
    case DT_INT32:   return 4;
    case DT_FLOAT32: return 4;
    case DT_FLOAT64: return 8;
    default: return 0;
  }
}


/**
 * @brief Ensure outbuf is RDMA-registered and synced from sendbuf if needed.
 *
 * Re-registers `outbuf` when its address or size differs from the last call,
 * updates the pg_handle metadata, and copies from `sendbuf` if they are
 * different buffers.
 *
 * @param pg   Process-group handle (holds RDMA context).
 * @param sendbuf Source data to copy if different from outbuf.
 * @param outbuf  Output buffer to register.
 * @param outbuf_total_bytes Size of outbuf in bytes.
 * @return 0 on success, -1 on registration failure.
 */
static int reg_outbuf_and_sync_sendbuf(pg_handle *pg, void *sendbuf, void *outbuf,
                                       const size_t total_bytes) {

  // Register only if the pointer or size has changed since the last call.
  if (pg->base_outbuf != outbuf || pg->outbuf_total_bytes != total_bytes) {
    // Deregister the old memory region to avoid leaks.
    if (pg->outbuf_mr)
      ibv_dereg_mr(pg->outbuf_mr);
    pg->outbuf_mr = ibv_reg_mr(pg->pd, outbuf, total_bytes,
                               IBV_ACCESS_LOCAL_WRITE | IBV_ACCESS_REMOTE_READ);
    if (!pg->outbuf_mr) {
      perror("ibv_reg_mr(outbuf)");
      return -1;
    }
    // Update handle metadata to reflect the new buffer and size.
    pg->base_outbuf   = outbuf;
    pg->outbuf_total_bytes = total_bytes;

    // If sendbuf is a different buffer, copy its contents into outbuf.
    if(sendbuf != outbuf) {
      memcpy(outbuf, sendbuf, total_bytes);
    }
  }
  return 0;
}

/**
 * @brief Apply a reduction operation element-wise, modifying the destination
 * buffer in place.
 *
 * Performs SUM, MIN, or MAX between two arrays of the same type and length.
 * The result overwrites the destination buffer.
 *
 * @param dst       Destination buffer, updated in place with the result.
 * @param src       Source buffer, read-only.
 * @param n_elems   Number of elements to process.
 * @param dt        Datatype of the elements (DT_INT32, DT_FLOAT32, DT_FLOAT64).
 * @param op        Reduction operation (OP_SUM, OP_MIN, OP_MAX).
 */
static void apply_op_inplace(void *dst, const void *src, size_t n_elems,
                             DATATYPE dt, OPERATION op)
{
  if (dt == DT_INT32) {
    int *d = (int*)dst; const int *s = (const int*)src;
    switch (op) {
      case OP_SUM: for (size_t i=0;i<n_elems;i++) d[i]+=s[i]; break;
      case OP_MIN: for (size_t i=0;i<n_elems;i++) if (s[i]<d[i]) d[i]=s[i]; break;
      case OP_MAX: for (size_t i=0;i<n_elems;i++) if (s[i]>d[i]) d[i]=s[i]; break;
    }
  } else if (dt == DT_FLOAT32) {
    float *d = (float*)dst; const float *s = (const float*)src;
    switch (op) {
      case OP_SUM: for (size_t i=0;i<n_elems;i++) d[i]+=s[i]; break;
      case OP_MIN: for (size_t i=0;i<n_elems;i++) if (s[i]<d[i]) d[i]=s[i]; break;
      case OP_MAX: for (size_t i=0;i<n_elems;i++) if (s[i]>d[i]) d[i]=s[i]; break;
    }
  } else if (dt == DT_FLOAT64) {
    double *d = (double*)dst; const double *s = (const double*)src;
    switch (op) {
      case OP_SUM: for (size_t i=0;i<n_elems;i++) d[i]+=s[i]; break;
      case OP_MIN: for (size_t i=0;i<n_elems;i++) if (s[i]<d[i]) d[i]=s[i]; break;
      case OP_MAX: for (size_t i=0;i<n_elems;i++) if (s[i]>d[i]) d[i]=s[i]; break;
    }
  }
}

/**
 * @brief Wait for a single successful work completion on a CQ.
 *
 * Polls the specified completion queue until one work completion (WC)
 * is returned with status IBV_WC_SUCCESS.
 *
 * @param cq  Pointer to the completion queue to poll.
 *
 * @return 0 on successful completion,
 *        -1 on poll failure or if the WC indicates an error.
 */
static int poll_one_cq(struct ibv_cq *cq, struct ibv_wc* wc) {
  while (1) {
    int n = ibv_poll_cq(cq, 1, wc); // Try to fetch 1 completion from the CQ
    if (n < 0) {
      perror("ibv_poll_cq");
      return -1;
    }
    if (n == 0) continue; // no completions available right now.
    if (wc->status != IBV_WC_SUCCESS) {
      fprintf(stderr, "WC error: %s (opcode=%d)\n",
              ibv_wc_status_str(wc->status), wc->opcode);
      return -1;
    }
    return 0;
  }
}

/**
 * @brief Post a single RDMA receive request.
 *
 * Prepares the NIC to receive up to `len` bytes of data on the given
 * queue pair and place it in the registered memory pointed to by `buf`.
 *
 * @param qp    Queue pair on which to post the receive.
 * @param recv_addr   Pointer to the local buffer (must be registered).
 * @param len   Number of bytes to receive.
 * @param lkey  Local key of the registered memory region for `buf`.
 * @param wrid  work id.
 *
 * @return 0 on success, -1 on failure
 */
static int post_recv(struct ibv_qp *qp, void *recv_addr,
                     uint32_t len, uint32_t lkey, uint64_t wrid) {
  // Describe the buffer to the NIC: address, length, and memory region key
  struct ibv_sge sge = { .addr=(uintptr_t)recv_addr, .length=len, .lkey=lkey };
  // Create a receive work request pointing to this SGE
  struct ibv_recv_wr wr = { .wr_id=wrid, .sg_list=&sge, .num_sge=1 };
  // For error reporting if posting fails
  struct ibv_recv_wr *bad = NULL;
  // Post the receive request to the queue pair
  if (ibv_post_recv(qp, &wr, &bad)) {
    perror("ibv_post_recv");
    return -1;
  }
  return 0;
}

/**
 * @brief Post a single RDMA send work request on a queue pair.
 *
 * @param qp    Queue pair on which to post the send.
 * @param send_addr   Pointer to the registered memory to send.
 * @param len   Number of bytes to send.
 * @param lkey  Local key for the registered memory region.
 * @param wrid work id.
 *
 * @return 0 on success, -1 on failure
 */
static int post_send(struct ibv_qp *qp, void *send_addr, uint32_t len,
                     uint32_t lkey, uint64_t wrid) {
  // Describe the buffer: address, size, and memory key
  struct ibv_sge sge = { .addr=(uintptr_t)send_addr, .length=len, .lkey=lkey };

  // Create and initialize a send work request
  struct ibv_send_wr wr = {0};
  wr.wr_id   = wrid;              // WR identifier
  wr.sg_list = &sge;           // List of scatter-gather entries
  wr.num_sge = 1;              // One buffer to send
  wr.opcode  = IBV_WR_SEND;    // Operation: SEND
  wr.send_flags = IBV_SEND_SIGNALED; // Request a completion entry

  struct ibv_send_wr *bad = NULL;   // For error reporting

  // Post the send request to the queue pair
  if (ibv_post_send(qp, &wr, &bad)) {
    perror("ibv_post_send");
    return -1;
  }

  return 0;
}

/**
 * @brief Post an RDMA READ request to fetch data from a remote peer.
 *
 * This function tells the local NIC to pull data directly from a
 * remote memory region (registered by the peer) into a local
 * registered buffer, without CPU involvement.
 *
 * @param qp          Queue Pair (RC) on which to issue the RDMA READ.
 * @param dst         Pointer to the local destination buffer
 *                    (must be registered).
 * @param len         Number of bytes to read from the remote memory.
 * @param lkey        Local key of the registered memory region for @p dst.
 * @param remote_start_addr Remote virtual address of the peer’s source buffer.
 * @param rkey        Remote key granting read access to @p remote_addr.
 * @param wrid        work id.
 *
 * @return 0 on success, or -1 if posting the work request fails.
 */
static int post_read(struct ibv_qp *qp, void *dst, uint32_t len, uint32_t lkey,
                     uint64_t remote_addr, uint32_t rkey, uint64_t wrid)
{
  // Describe the local buffer (destination for the READ)
  struct ibv_sge sge = { .addr=(uintptr_t)dst, .length=len, .lkey=lkey };

  // Create and initialize a send work request
  struct ibv_send_wr wr = {0};
  wr.wr_id   = wrid;                        // Work request identifier
  wr.sg_list = &sge; wr.num_sge = 1;     // One buffer in the scatter-gather list
  wr.opcode  = IBV_WR_RDMA_READ;         // Operation: RDMA READ
  wr.send_flags = IBV_SEND_SIGNALED;     // Request a completion entry

  // Set remote buffer info (address + rkey from peer's ctrl_hdr)
  wr.wr.rdma.remote_addr = remote_addr;
  wr.wr.rdma.rkey        = rkey;

  struct ibv_send_wr *bad = NULL;

  // Post the READ request to the QP
  if (ibv_post_send(qp, &wr, &bad)) {
    perror("ibv_post_send(READ)");
    return -1;
  }
  return 0;
}

/**
 * @brief Synchronize all ranks between ring steps with a tiny ACK handshake.
 *
 * Each process:
 *   1. Posts a 1-byte receive from its LEFT neighbor.
 *   2. Sends a 1-byte token to its RIGHT neighbor.
 *   3. Waits until both send and receive completions arrive.
 *
 * This acts as a lightweight barrier between pipeline phases.
 *
 * @param pg  Active process-group handle.
 *
 * @return 0 on success, -1 on error.
 */
static int ack_exchange(pg_handle *pg) {
  struct ibv_wc wc;

  // Post RECV from LEFT
  if(post_recv (pg->qp_left, pg->ack_recv_buf, 1, pg->ack_recv_mr->lkey,
                WRID_ACK_RECV) != 0) return -1;

  // SEND to RIGHT
  *(pg->ack_send_buf) = 0xAC; // any token
  if(post_send (pg->qp_right, pg->ack_send_buf, 1, pg->ack_send_mr->lkey,
                WRID_ACK_SEND) != 0) return -1;

  // Wait for both completions
  int got_recv = 0, got_send = 0;
  while (!(got_recv && got_send)) {
    if (poll_one_cq(pg->cq, &wc) != 0) return -1;
    if (wc.wr_id == WRID_ACK_RECV) got_recv = 1;
    else if (wc.wr_id == WRID_ACK_SEND) got_send = 1;
  }
  return 0;
}

/**
 * @brief Round a value down to the nearest multiple of @p align.
 *
 * If @p align is zero, the value is returned unchanged.
 *
 * @param x      Value to round down.
 * @param align  Alignment boundary (must be > 0 for effect).
 * @return       Largest multiple of @p align not greater than @p x.
 */
static inline size_t round_down(size_t x, size_t align) {
  return (align == 0) ? x : (x / align) * align;
}

/**
 * @brief Choose a chunk size (in bytes) for pipelined transfers.
 *
 * @param element_size  Size of one element in bytes.
 * @param block_bytes   Total size of the block in bytes.
 * @return Chunk size in bytes (aligned and nonzero).
 */
static size_t choose_chunk_bytes(size_t element_size,
                                 size_t block_bytes)
{
  if (element_size == 0) return 0;

  // Never larger than the block
  size_t chunk_bytes = (MAX_CHUNK_BYTES > block_bytes) ?
                       block_bytes : MAX_CHUNK_BYTES;

  // Align down to element_size
  size_t aligned_chunk_bytes = round_down(chunk_bytes, element_size);

  // Guard: if rounded-down became 0, pick one element
  if (aligned_chunk_bytes == 0) aligned_chunk_bytes = element_size;

  return aligned_chunk_bytes;
}



/**
 * @brief Send a block to the right neighbor and receive one from the left.
 *
 * Posts a RECV from the left QP (into staging if in reduce-scatter phase,
 * otherwise directly into recv_ptr), and a SEND to the right QP. Waits for
 * both completions before returning.
 *
 * @param pg                   Process group handle with QPs, MRs, and CQ.
 * @param send_ptr             Pointer to the block to send.
 * @param recv_ptr             Pointer to the buffer for the incoming block.
 * @param block_bytes          Size of the block in bytes.
 * @param reduce_scatter_phase If true, receive into staging buffer for later reduction.
 * @return 0 on success, -1 on error.
 */
static int eager_ring_exchange_block(pg_handle *pg,
                                     uint8_t *send_ptr,
                                     uint8_t *recv_ptr,
                                     size_t block_bytes,
                                     bool reduce_scatter_phase)
{
  struct ibv_wc wc;

  // Post RECV: either into staging buffer (reduce) or directly into recv_ptr
  void *dst_ptr = reduce_scatter_phase ? pg->base_staging_recv : recv_ptr;
  uint32_t dst_lkey = reduce_scatter_phase ? pg->staging_mr->lkey :
      pg->outbuf_mr->lkey;

  // Post receive BEFORE send to avoid message arrival before buffer is ready
  if (post_recv(pg->qp_left, dst_ptr, (uint32_t)block_bytes, dst_lkey, 0))
    return -1;

  // Post SEND to right neighbor
  if (post_send(pg->qp_right, send_ptr, (uint32_t)block_bytes,
                pg->outbuf_mr->lkey, 0))
    return -1;

  /* Wait for both completions. Order of completions is unpredictable,
  so we track both */
  bool got_recv = false, got_send = false;
  while (!got_recv || !got_send) {
    if (poll_one_cq(pg->cq, &wc)) return -1;
    if (wc.opcode == IBV_WC_RECV) got_recv = true;
    else if (wc.opcode == IBV_WC_SEND) got_send = true;
  }
  return 0;
}

/**
 * @brief Eager ring reduce-scatter.
 *
 * Each rank sends its current block to the right neighbor and
 * receives the next block from the left, reducing the received
 * data in-place using the given operation.
 *
 * @param outbuf        Buffer with local input; overwritten with this rank's reduced block.
 * @param element_count Total number of elements across all ranks.
 * @param datatype      Element type (e.g., INT, FLOAT).
 * @param op            Reduction operation (e.g., SUM, MAX).
 * @param pg            Process-group handle (RDMA resources).
 * @param num_processes Total number of ranks in the ring.
 * @param my_rank       Rank of this process.
 * @param element_size  Size of one element in bytes.
 *
 * @return 0 on success, -1 on failure.
 */
static int eager_reduce_scatter(void *outbuf, int element_count,
                                DATATYPE datatype,
                                OPERATION op, pg_handle *pg,
                                int num_processes, int my_rank,
                                size_t element_size)
{
  // Calculate the size of each rank's block
  const size_t block_elems = (size_t)element_count / num_processes;
  const size_t block_bytes = block_elems * element_size;

  for (int step = 0; step < num_processes - 1; ++step) {
    // the block we currently have and will send
    int send_index = (my_rank - step + num_processes) % num_processes;
    uint8_t *send_ptr = (uint8_t*)outbuf + (size_t)send_index * block_bytes;

    // send block to right neighbor and receive block from left neighbor to staging
    if (eager_ring_exchange_block(pg, send_ptr, NULL,
                                  block_bytes, true))
      return -1;

    // the block we will receive and reduce
    int recv_index = (my_rank - step - 1 + num_processes) % num_processes;
    uint8_t *dst_ptr  = (uint8_t*)outbuf + (size_t)recv_index * block_bytes;

    apply_op_inplace(dst_ptr, pg->base_staging_recv,
                     block_elems, datatype, op);
  }
  return 0;
}


/**
 * @brief Eager ring all-gather.
 *
 * Circulates each reduced block around the ring so every rank
 * collects the full final result.
 *
 * @param outbuf        Buffer holding this rank's reduced block; filled with all blocks.
 * @param element_count Total number of elements across all ranks.
 * @param pg            Process-group handle (RDMA resources).
 * @param num_processes Total number of ranks in the ring.
 * @param my_rank       Rank of this process.
 * @param element_size  Size of one element in bytes.
 *
 * @return 0 on success, -1 on failure.
 */
static int eager_all_gather(void *outbuf,
                            int element_count, pg_handle *pg,
                            int num_processes, int my_rank,
                            size_t element_size)
{
  const size_t block_elems = (size_t)element_count / num_processes;
  const size_t block_bytes = block_elems * element_size;
  for (int step = 0; step < num_processes - 1; ++step) {
    // Different block indexing than reduce-scatter
    int send_index = (my_rank - step + 1 + num_processes) % num_processes;
    int recv_index = (my_rank - step + num_processes) % num_processes;

    uint8_t *send_ptr = (uint8_t*)outbuf + (size_t)send_index * block_bytes;
    uint8_t *recv_ptr  = (uint8_t*)outbuf + (size_t)recv_index * block_bytes;

    // Exchange blocks (recv directly to final position, no reduction)
    if (eager_ring_exchange_block(pg, send_ptr, recv_ptr,
                                  block_bytes, false))
      return -1;
  }
  return 0;
}



/**
 * @brief Exchange RDMA buffer descriptors with neighbors.
 *
 * Posts a RECV for the left neighbor’s control header, then sends this
 * process’s buffer info (address, rkey, size) to the right neighbor.
 * Waits for both SEND and RECV completions. On success, returns the
 * left neighbor’s buffer address and rkey via output parameters.
 *
 * @param pg               Process group handle.
 * @param outbuf           Pointer to this process’s output buffer.
 * @param total_bytes      Size of the output buffer in bytes.
 * @param left_remote_addr Output: left neighbor’s buffer address.
 * @param left_remote_rkey Output: left neighbor’s rkey.
 * @return 0 on success, -1 on error.
 */
static int exchange_control_headers(pg_handle *pg, void *outbuf,
                                    size_t total_bytes,
                                    uint64_t *left_remote_addr,
                                    uint32_t *left_remote_rkey) {
  struct ibv_wc wc;

  if(post_recv(pg->qp_left, pg->base_ctrl_recv, sizeof(struct ctrl_hdr),
               pg->ctrl_recv_mr->lkey, WRID_CTRL_RECV) != 0) {
    return -1;
  }

  /* Fill and SEND our ctrl header to RIGHT:We let the neighbor READ from our outbuf */
  pg->base_ctrl_send->remote_addr = (uint64_t)(uintptr_t)outbuf;
  pg->base_ctrl_send->rkey        = pg->outbuf_mr->rkey;
  pg->base_ctrl_send->nbytes      = (uint32_t)total_bytes;
  if (post_send(pg->qp_right, pg->base_ctrl_send, sizeof(struct ctrl_hdr),
                pg->ctrl_send_mr->lkey, WRID_CTRL_SEND) != 0) {
    return -1;
  }

  // Wait for RECV ctrl and SEND ctrl to complete
  if (poll_one_cq(pg->cq, &wc) != 0) {
    return -1; // RECV ctrl done
  }
  if (poll_one_cq(pg->cq, &wc) != 0) {
    return -1; // SEND ctrl done
  }

  *left_remote_addr = pg->base_ctrl_recv->remote_addr;
  *left_remote_rkey = pg->base_ctrl_recv->rkey;
  return 0;
}



/**
 * @brief Post a single RDMA READ chunk into the staging buffer.
 *
 * Calculates the next chunk’s offset and size within a block and issues
 * an RDMA READ from the left neighbor into the appropriate staging slot.
 * Updates the caller’s remaining-bytes counter on success.
 *
 * @param pg               Process-group handle with QP, MR, and chunk info.
 * @param remote_block_base Base remote address of the neighbor’s block.
 * @param left_remote_rkey  Remote key granting RDMA READ access.
 * @param chunk_index_in_block       Index of the chunk within the current block.
 * @param block_bytes       Total bytes in this block.
 * @param remaining_bytes   Pointer to remaining bytes counter; decremented.
 *
 * @return 0 on success, -1 if the RDMA READ post fails.
 */
static int post_read_chunk_to_staging(pg_handle *pg,
                                      uint64_t remote_block_base,
                                      uint32_t left_remote_rkey,
                                      uint32_t chunk_index_in_block,
                                      size_t block_bytes,
                                      size_t *remaining_bytes)
{
  //
  const size_t chunk_offset  = (size_t)chunk_index_in_block * pg->chunk_bytes;
  // Caller guarantees chunk_index < num_chunks_in_block so left > 0
  const size_t this_chunk_bytes =
      (chunk_offset + pg->chunk_bytes <= block_bytes) ?
      pg->chunk_bytes : (block_bytes - chunk_offset);

  // Map chunk index to a pipeline slot and create a unique work request ID
  const uint32_t slot = chunk_index_in_block % pg->max_pipe_depth;
  const uint64_t wrid = WRID(slot, chunk_index_in_block);

  // Destination address in the staging buffer for this slot
  void *dst = pg->base_staging_recv + (size_t)slot * pg->chunk_bytes;

  if(post_read(pg->qp_left,
                   dst, this_chunk_bytes, pg->staging_mr->lkey,
                   remote_block_base + chunk_offset,
                   left_remote_rkey, wrid))
    return -1;
  *remaining_bytes -= this_chunk_bytes;
  return 0;
}


/**
 * @brief Rendezvous reduce-scatter using pipelined RDMA reads.
 *
 * Each process fetches the block it needs from its left neighbor via RDMA READ,
 * reduces it into its local buffer, and repeats until all blocks are reduced.
 * The reads are pipelined with depth pg->max_pipe_depth to overlap transfer
 * and computation.
 *
 * @param pg                    Process group handle with QPs, MRs, etc.
 * @param outbuf                Local output buffer (also holds partial results).
 * @param block_bytes           Size of one block in bytes.
 * @param num_chunks_in_block   Number of pipeline chunks per block.
 * @param left_remote_addr      Base address of left neighbor’s buffer.
 * @param left_remote_rkey      RKey for left neighbor’s buffer.
 * @param element_size          Size of one element in bytes.
 * @param datatype              Element datatype.
 * @param operation             Reduction operation to apply.
 * @param num_processes         Total number of processes in the ring.
 * @param my_rank               This process’s rank in the ring.
 * @return 0 on success, -1 on error.
 */
static int rendezvous_reduce_scatter(pg_handle *pg,
                                     void *outbuf,
                                     size_t block_bytes,
                                     uint32_t num_chunks_in_block,
                                     uint64_t left_remote_addr,
                                     uint32_t left_remote_rkey,
                                     size_t element_size,
                                     DATATYPE datatype,
                                     OPERATION operation,
                                     int num_processes,
                                     int my_rank)
{
  struct ibv_wc wc;

  for (int step = 0; step < num_processes - 1; ++step) {
    // Determine which block this rank should receive/reduce in this step
    int recv_block_index = (my_rank - step - 1 + num_processes) % num_processes;

    // Calculate the remote base address of the block to read from the left neighbor
    uint64_t remote_block_base = left_remote_addr +
                                 (size_t)recv_block_index * block_bytes;


    // --- Post initial READ window (fill pipeline with up to max_pipe_depth) ---
    uint32_t num_chunks_posted = 0; // Number of RDMA READs already posted
    uint32_t num_chunks_completed = 0; // Number of RDMA READ completions processed
    size_t remaining_bytes = block_bytes;

    // Determine how many chunks to post initially (limited by pipeline depth)
    const uint32_t first_num_chunks =
        (pg->max_pipe_depth < (uint32_t)num_chunks_in_block) ?
        pg->max_pipe_depth : (uint32_t)num_chunks_in_block;

    for (; num_chunks_posted < first_num_chunks; num_chunks_posted++) {
      if (post_read_chunk_to_staging(pg,
          /*remote_block_base=*/remote_block_base,
          /*left_remote_rkey=*/left_remote_rkey,
          /*chunk_index_in_block=*/num_chunks_posted,
          /*block_bytes=*/block_bytes, &remaining_bytes) != 0)
        return -1;
    }

    // --- Drive the pipeline until all chunks are processed ---
    while (num_chunks_completed < (uint32_t)num_chunks_in_block) {
      // Wait for next READ completion
      if (poll_one_cq(pg->cq, &wc) != 0) return -1;

      const uint64_t wrid     = wc.wr_id;
      const uint32_t slot     = WRID_SLOT(wrid);
      const uint32_t chunk_idx_in_block = WRID_CHUNKIDX(wrid);

      // Reduce from staging slot into final destination buffer
      const size_t chunk_offset = (size_t)chunk_idx_in_block * pg->chunk_bytes;
      const size_t this_chunk_bytes =
          (chunk_offset + pg->chunk_bytes <= block_bytes) ?
          pg->chunk_bytes : (block_bytes - chunk_offset);
      // Calculate the local base address where the received block will be reduced into
      uint8_t *outbuf_block_base = (uint8_t*)outbuf +
                                   (size_t)recv_block_index * block_bytes;
      void *dst = outbuf_block_base + chunk_offset;
      void *src = pg->base_staging_recv + (size_t)slot * pg->chunk_bytes;
      apply_op_inplace(dst, src, this_chunk_bytes / element_size,
                       datatype, operation);

      ++num_chunks_completed;

      // Post next READ if more chunks remain
      if (num_chunks_posted < (uint32_t)num_chunks_in_block) {
        if (post_read_chunk_to_staging(pg,
            /*remote_block_base=*/remote_block_base,
            /*left_remote_rkey=*/left_remote_rkey,
            /*chunk_index_in_block=*/num_chunks_posted,
            /*block_bytes=*/block_bytes, &remaining_bytes) != 0)
          return -1;
        ++num_chunks_posted;
      }
    }

    /* Exchange ACKs to ensure neighbor isn't reading data that we're still
     * updating(reading/reducing) */
    if (ack_exchange(pg) != 0) return -1;
  }
  return 0;
}



/*
 * The key difference between the all-gather and reduce-scatter
 * implementations is how the incoming data is buffered:
 * during reduce-scatter each RDMA READ first lands in the staging buffer,
 * because we must combine the remote chunk with our local data before writing
 * it to outbuf.  In contrast, all-gather performs no reduction, so RDMA READs
 * are posted directly into outbuf and the data is ready immediately.
 * In summary:
 * reduce-scatter = staging + reduce, all-gather = direct to outbuf.
 */

/**
 * @brief Rendezvous all-gather using pipelined RDMA reads.
 *
 * Each process fetches blocks from its left neighbor via RDMA READ and
 * places them directly into its output buffer. Uses a pipelined window
 * of depth pg->max_pipe_depth to overlap reads. No reduction is done in
 * this phase.
 *
 * @param pg                    Process group handle with QPs, MRs, etc.
 * @param outbuf                Local output buffer.
 * @param block_bytes           Size of one block in bytes.
 * @param left_remote_addr      Base address of left neighbor’s buffer.
 * @param left_remote_rkey      RKey for left neighbor’s buffer.
 * @param num_processes         Total number of processes in the ring.
 * @param my_rank               This process’s rank in the ring.
 * @return 0 on success, -1 on error.
 */
static int rendezvous_all_gather(pg_handle *pg,
                                 void *outbuf,
                                 size_t block_bytes,
                                 uint64_t left_remote_addr,
                                 uint32_t left_remote_rkey,
                                 int num_processes,
                                 int my_rank)
{
  struct ibv_wc wc;

  for (int step = 0; step < num_processes - 1; ++step) {
    /* Calculate which block index to receive this step.
    * Blocks rotate clockwise: at step s, we receive block (my_rank - s) modP */
    int recv_block_index = (my_rank - step + num_processes) % num_processes;
    uint64_t remote_block_base = left_remote_addr +
                                 (uint64_t)recv_block_index * block_bytes;
    // Calculate local destination: where this block goes in our buffer
    uint8_t *outbuf_block_base = (uint8_t*)outbuf +
                                 (size_t)recv_block_index * block_bytes;
    const uint64_t wrid = WRID(0, step);

    if(post_read(pg->qp_left, outbuf_block_base, block_bytes, pg->outbuf_mr->lkey,
                 remote_block_base, left_remote_rkey, wrid))
      return -1;

    /* Wait for completion of this block’s READ */
    if (poll_one_cq(pg->cq, &wc) != 0) {
      return -1;
    }

    /* Exchange ACKs to ensure neighbor has finished reading our data before
    we move to the next step and potentially overwrite it */
    if (ack_exchange(pg) != 0) return -1;
  }

  return 0;
}

/**
 * @brief Ring all-reduce: reduce then broadcast to all ranks.
 *
 * Splits the global array evenly across ranks, then:
 *   • **Reduce-Scatter** – each rank fetches and reduces data so it
 *     ends with its own reduced block (eager for small messages,
 *     RDMA rendezvous for large).
 *   • **All-Gather** – circulates those reduced blocks so every rank
 *     obtains the complete reduced result (same eager/rendezvous choice).
 *
 * @param sendbuf               Input data for this rank.
 * @param outbuf                Output buffer for the final reduced array.
 * @param outbuf_total_bytes    Size of outbuf in bytes.
 * @param element_count         Total number of elements to reduce.
 * @param datatype              Element type.
 * @param operation             Reduction operation (e.g. SUM, MAX).
 * @param pg_handle_void        Process-group handle from connect_process_group().
 * @return 0 on success, -1 on parameter or RDMA error.
 */

int pg_all_reduce(void *sendbuf, void *outbuf, int element_count,
                  DATATYPE datatype, OPERATION operation,
                  void *pg_handle_void) {
  pg_handle *pg = (pg_handle*)pg_handle_void;
  if (!pg || !sendbuf || !outbuf || element_count <= 0) return -1;

  const size_t element_size = dt_size(datatype);
  if (element_size == 0) {
    fprintf(stderr,"Unsupported DATATYPE\n");
    return -1;
  }

  const int num_processes = pg->nprocs;
  const int my_rank = pg->rank;
  if (element_count % num_processes != 0) {
    fprintf(stderr,"element count (%d) must be divisible by num of processes "
                   "(%d)\n", element_count, num_processes);
    return -1;
  }

  const size_t total_bytes = (size_t)element_count * element_size;

  // Each rank holds one "block" of the array
  const size_t block_elements = (size_t)element_count / num_processes;
  const size_t block_bytes = block_elements * element_size;

  pg->chunk_bytes = choose_chunk_bytes (element_size, block_bytes);
  const uint32_t num_chunks_in_block = (uint32_t)(
      (block_bytes + pg->chunk_bytes - 1) / pg->chunk_bytes);

  if (reg_outbuf_and_sync_sendbuf(pg, sendbuf, outbuf, total_bytes) != 0) {
    return -1;
  }

  uint64_t left_remote_addr;
  uint32_t left_remote_rkey;

  // ============= REDUCE-SCATTER PHASE =============
  if (block_bytes <= pg->total_staging_bytes) {
    if (eager_reduce_scatter (outbuf, element_count,
                              datatype, operation, pg,
                              num_processes, my_rank, element_size))
      return -1;
  }
  else {
    if (exchange_control_headers(pg, outbuf, total_bytes,
                                 &left_remote_addr, &left_remote_rkey) != 0)
      return -1;
    if (rendezvous_reduce_scatter(pg, outbuf, block_bytes,
                                  num_chunks_in_block,
                                  left_remote_addr, left_remote_rkey,
                                  element_size, datatype, operation,
                                  num_processes, my_rank) != 0)
      return -1;
  }

  // ============= ALL-GATHER PHASE =============
  if (block_bytes <= pg->total_staging_bytes) {
    if (eager_all_gather (outbuf, element_count, pg,
                          num_processes, my_rank, element_size))
      return -1;
  }
  else {
    if (exchange_control_headers(pg, outbuf, total_bytes,
                                 &left_remote_addr, &left_remote_rkey) != 0)
      return -1;
    if (rendezvous_all_gather(pg, outbuf, block_bytes,
                              left_remote_addr, left_remote_rkey,
                              num_processes, my_rank) != 0)
      return -1;
  }
  return 0;
}

/**
 * @brief Close and free all resources associated with a process group handle.
 *
 * This function destroys all RDMA verbs objects (QPs, CQ, MR, PD, context),
 * frees the staging buffer, closes TCP sockets (if still open), and finally
 * frees the pg_handle structure itself.
 *
 * @param pg_handle  Pointer returned by connect_process_group().
 * @return 0 on success.
 */
int close_pg_handle(pg_handle *pg) {
  if (!pg) return 0;

  if (pg->left_fd >= 0) {
    close(pg->left_fd);
    pg->left_fd = -1;
  }
  if (pg->right_fd >= 0) {
    close(pg->right_fd);
    pg->right_fd = -1;
  }

  if (pg->ctrl_send_mr) {
    if (ibv_dereg_mr(pg->ctrl_send_mr))
      perror("ibv_dereg_mr");
    pg->ctrl_send_mr = NULL;
  }

  if (pg->base_ctrl_send) {
    free (pg->base_ctrl_send);
    pg->base_ctrl_send = NULL;
  }

  if (pg->ctrl_recv_mr) {
    if (ibv_dereg_mr(pg->ctrl_recv_mr))
      perror("ibv_dereg_mr");
    pg->ctrl_recv_mr = NULL;
  }

  if (pg->base_ctrl_recv) {
    free (pg->base_ctrl_recv);
    pg->base_ctrl_recv = NULL;
  }

  if (pg->ack_recv_mr) {
    if (ibv_dereg_mr(pg->ack_recv_mr))
      perror("ibv_dereg_mr");
    pg->ack_recv_mr = NULL;
  }

  if (pg->ack_recv_buf) {
    free (pg->ack_recv_buf);
    pg->ack_recv_buf = NULL;
  }

  if (pg->ack_send_mr) {
    if (ibv_dereg_mr(pg->ack_send_mr))
      perror("ibv_dereg_mr");
    pg->ack_send_mr = NULL;
  }

  if (pg->ack_send_buf) {
    free (pg->ack_send_buf);
    pg->ack_send_buf = NULL;
  }

  if (pg->staging_mr) {
    if (ibv_dereg_mr(pg->staging_mr))
      perror("ibv_dereg_mr");
    pg->staging_mr = NULL;
  }

  if (pg->base_staging_recv) {
    free (pg->base_staging_recv);
    pg->base_staging_recv = NULL;
  }

  if (pg->outbuf_mr) {
    if (ibv_dereg_mr(pg->outbuf_mr))
      perror("ibv_dereg_mr");
    pg->outbuf_mr = NULL;
  }

  if (pg->qp_left) {
    if (ibv_destroy_qp(pg->qp_left))
      perror("ibv_destroy_qp(left)");
    pg->qp_left = NULL;
  }

  if (pg->qp_right) {
    if (ibv_destroy_qp(pg->qp_right))
      perror("ibv_destroy_qp(right)");
    pg->qp_right = NULL;
  }

  if (pg->cq) {
    if (ibv_destroy_cq(pg->cq))
      perror("ibv_destroy_cq");
    pg->cq = NULL;
  }

  if (pg->pd) {
    if (ibv_dealloc_pd(pg->pd))
      perror("ibv_dealloc_pd");
    pg->pd = NULL;
  }

  if (pg->ctx) {
    if (ibv_close_device(pg->ctx))
      perror("ibv_close_device");
    pg->ctx = NULL;
  }

  free(pg);
  return 0;
}