#include <sys/types.h>

#ifndef NETHEADERS_H
#define NETHEADERS_H

/* Ethernet header */
struct ethernet_header {
  /* Destination address */
  u_int8_t ether_dhost[6];

  /* Source address */
  u_int8_t ether_shost[6];

  /* Payload type */
  u_int16_t ether_type;
};

#define ETHERTYPE_IP 0x0800
#define ETHERTYPE_ARP 0x0806     
#define ARPHDR_ETHER 0x0001

#define IP_ADDR_LEN 4
#ifndef ETHER_ADDR_LEN
#define ETHER_ADDR_LEN 6 
#endif

/* ARP/RARP header */
struct arp_header  {

  /* Format of hardware address */
  u_int16_t hardware; 

  /* Format of protocol address */
  u_int16_t protocol; 

  /* Length of hardware address */
  u_int8_t hardware_length;

  /* Length of protocol address */
  u_int8_t protocol_length;

  /* ARP Operation type */
  u_int16_t operation; 
};

/* ARP payload */ 
struct  arp_payload {
  u_int8_t sha[ETHER_ADDR_LEN]; /* Sender hardware address */
  u_int8_t spa[IP_ADDR_LEN]; /* Sender protocol address */
  u_int8_t tha[ETHER_ADDR_LEN]; /* Target hardware address */
  u_int8_t tpa[IP_ADDR_LEN]; /* Target protocol address */
};


      
/* IP header  */
struct ip_header {

#if BYTE_ORDER == LITTLE_ENDIAN
  /* Header length + protocol version */
  u_int8_t hl:4, v:4;
#else
  /* Protocol version + header length */
  u_int8_t  v:4, hl:4;
#endif

  /* Type of service */
  u_int8_t tos;

  /* Total length */
  u_int16_t len;

  /* ID */
  u_int16_t id;

  /* Fragment offset */
  u_int16_t off;

  /* Time to live */
  u_int8_t ttl;

  /* Protocol */
  u_int8_t p;

  /* Checksum */
  u_int16_t sum;

  /* Source address */
  u_int8_t src[4];

  /* Destination address */
  u_int8_t dst[4];
};


/* ICMP header */
struct icmp_header {
  /* Type of message */
  u_int8_t type;    

  /* Type sub code */
  u_int8_t code;

  /* Checksum */
  u_int16_t checksum;

  union {
    struct {
      u_int16_t id;
      u_int16_t sequence;
    } echo;                     /* echo datagram */
    u_int32_t   gateway;        /* gateway address */
    struct {
      u_int16_t unused;
      u_int16_t mtu;
    } frag;                     /* path mtu discovery */
  } un;
};


/* TCP header */
struct tcp_header {
  /* Source port */
  u_int16_t src;

  /* Destination port */
  u_int16_t dst;

  /* Sequence number */
  u_int32_t seqn;

  /* Acknowledgement number */
  u_int32_t ackn;

  /* Data offset */
#if BYTE_ORDER == LITTLE_ENDIAN 
  /* (unused) (4 bits) + header length in 32 bits words (4 bits) */
  u_int8_t x2:4, len:4; 
#else
  /* Header length in 32 bits words (4 bits) + (unused) (4 bits) */
  u_int8_t len:4, x2:4;  
#endif
  
  /* Flags */
  u_int8_t flags;

  /* Window */
  u_int16_t window;

  /* Checksum */
  u_int16_t checksum;

  /* Urgent pointer */
  u_int16_t urgent_ptr;
};

#define TH_FIN        0x01
#define TH_SYN        0x02
#define TH_RST        0x04
#define TH_PSH        0x08
#define TH_ACK        0x10
#define TH_URG        0x20


/* UDP header */
struct udp_header {

  /* Source port */
  u_int16_t src;

  /* Destination port */
  u_int16_t dst;

  /* Header Length */
  u_int16_t length;

  /* UDP Checksum */
  u_int16_t checksum;
};


/* DNS header */
struct dns_header {
  /* Request ID */
  u_int16_t id;

  /* Flags */
#if BYTE_ORDER == LITTLE_ENDIAN 
  u_int16_t rcode:4, /* Response code */
    z:3, /* Reserved */
    ra:1, /* Recursion available */ 
    rd:1, /* Recursion desired */
    tc:1, /* Flag that specifies that the message has been truncated and TCP should be used instead */ 
    aa:1, /* Flag set if the answer is authoritative */
    opcode:4, /* 0 is standard query, all other values are not interesting */
    qr:1; /* 0 is question, 1 is response */
#else
  u_int16_t qr:1, /* 0 is question, 1 is response */
    opcode:4, /* 0 is standard query, all other values are not interesting */
    aa:1, /* Flag set if the answer is authoritative */
    tc:1, /* Flag that specifies that the message has been truncated and TCP should be used instead */ 
    rd:1, /* Recursion desired */
    ra:1, /* Recursion available */ 
    z:3, /* Reserved */
    rcode:4; /* Response code */
#endif

  u_int16_t questions; /* Question count */
  u_int16_t answers; /* Answers count */
  u_int16_t authority; /* Resource records in the Authority section */
  u_int16_t additional; /* Additional resource records */
};

#define DNS_RCODE_NOERROR        0
#define DNS_RCODE_FORMATERROR    1
#define DNS_RCODE_SERVERFAILURE    2
#define DNS_RCODE_NAMEERROR      3
#define DNS_RCODE_NOTIMPLEMENTED 4
#define DNS_RCODE_REFUSED 5
#define DNS_RCODE_YXDOMAIN 6
#define DNS_RCODE_YXRRSET 7
#define DNS_RCODE_NXRRSET 8
#define DNS_RCODE_NOTAUTH 9
#define DNS_RCODE_NOTZONE 10

#define DNS_QTYPE_A 1
#define DNS_QTYPE_PTR 12

#define DNS_QCLASS_IN 1
#endif
