#ifndef _LIB_ALL_REDUCE_H_
#define _LIB_ALL_REDUCE_H_

#include <infiniband/verbs.h>
#include <arpa/inet.h>
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <netdb.h>
#include <poll.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>
#include <stdbool.h>

#ifndef NI_MAXHOST
#define NI_MAXHOST 1025
#endif

#define WIRE_STR_LEN (sizeof "0000:000000:000000:00000000000000000000000000000000")
#define BASE_PORT 12345     // Each rank listens on BASE_PORT + rank

#define QP_ATTR_MIN_RNR 1
#define QP_ATTR_TIMEOUT 20
#define QP_ATTR_RETRY_CNT 7
#define QP_ATTR_RNR_RETRY 7

#define MAX_CHUNK_BYTES 32<<10



#define WRID_CTRL_RECV 0xC7A10001ULL
#define WRID_CTRL_SEND 0xC7A10002ULL
#define WRID_ACK_RECV 0xC7A1AA01ULL
#define WRID_ACK_SEND 0xC7A1AA02ULL

#define WRID(slot, chunk_index)  ( (uint64_t)(((uint64_t)(slot) << 32) | (uint32_t)(chunk_index)) )
#define WRID_SLOT(wrid)          ( (uint32_t)((wrid) >> 32) )
#define WRID_CHUNKIDX(wrid)      ( (uint32_t)((wrid) & 0xffffffffu) )

typedef struct rdma_ep {
    uint16_t       lid;
    uint32_t       qpn;
    uint32_t       psn;
    union ibv_gid  gid;
} rdma_ep;

/* Small control header used for rendezvous handshake */
typedef struct ctrl_hdr {
    uint64_t remote_addr;  /* virtual address of buffer to READ from*/
    uint32_t rkey;         /* remote key (grants access) */
    uint32_t nbytes;       /* size of the buffer */
} ctrl_hdr;

typedef struct pg_handle {
    // TCP
    int left_fd, right_fd;
    int rank, nprocs;

    // Verbs core
    struct ibv_context *ctx;
    struct ibv_pd      *pd;
    struct ibv_cq      *cq;
    // QPs to neighbors
    struct ibv_qp      *qp_left;
    struct ibv_qp      *qp_right;

    // Port / addressing
    uint8_t             ib_port;
    struct rdma_ep      local_left;   // what we advertise for the left QP
    struct rdma_ep      local_right;  // what we advertise for the right QP
    struct rdma_ep      remote_left;  // what the left neighbor advertised
    struct rdma_ep      remote_right; // what the right neighbor advertised

    uint32_t max_pipe_depth;

    struct ibv_mr *outbuf_mr;
    uint8_t *base_outbuf;
    size_t outbuf_total_bytes;

    // --- control buffers (SEND/RECV of ctrl_hdr) ---
    struct ctrl_hdr *base_ctrl_send;
    struct ctrl_hdr *base_ctrl_recv;
    struct ibv_mr   *ctrl_send_mr;
    struct ibv_mr   *ctrl_recv_mr;

    // --- staging for RDMA READ pipeline ---
    uint8_t *base_staging_recv;     // base of slots
    size_t   chunk_bytes;
    size_t   total_staging_bytes;    // MAX_CHUNK_BYTES * max_pipe_depth
    struct ibv_mr *staging_mr;

    // --- ack buffers for per-step eager fence ---
    uint8_t       *ack_send_buf;
    uint8_t       *ack_recv_buf;
    struct ibv_mr *ack_send_mr;
    struct ibv_mr *ack_recv_mr;

} pg_handle;

typedef enum {
    DT_INT32 = 0,
    DT_FLOAT32 = 1,
    DT_FLOAT64 = 2
} DATATYPE;

typedef enum {
    OP_SUM = 0,
    OP_MIN = 1,
    OP_MAX = 2
} OPERATION;

int connect_process_group(const char *server_list, void **pg_handle_out);
int pg_all_reduce(void *sendbuf, void *recvbuf,
                  int element_count, DATATYPE datatype,
                  OPERATION operation,
                  void *pg_handle_void);
int close_pg_handle(pg_handle *handle);
#endif //_LIB_ALL_REDUCE_H_
