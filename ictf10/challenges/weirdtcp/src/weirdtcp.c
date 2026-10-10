#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <pcap.h>
#include <libnet.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <net/ethernet.h>
#ifdef HAVE_NETINET_ETHER_H
#include <netinet/ether.h>
#endif
#include "mydiag.h"
#include "netheaders.h"

#define DEFAULT_NETMASK "255.255.255.0"

#define ERR_WRONG_PARAMS 10
#define ERR_SETUP 11
#define ERR_LIBNET 12

#define IPPROTO_MINE 143

#define TIME_THRESHOLD 20 /* Window for an acceptable response */
#define MAXBUFSIZE 1024 /* Maximum size of file contents */
/* #define DEBUG*/


/*
 * GLOBALS
 */
u_int8_t host_eth_addr[ETHER_ADDR_LEN]; /* Ethernet address of the impersonated host */ 
u_int32_t host_ip_addr; /* IP address of the impersonated host, in net byte order */
u_int32_t trusted_ip_addr; /* IP address of the trusted host, in net byte order */
char *device = NULL; /* The device to sniff on */
u_int16_t ip_id = 0; /* The IP identifier to be used */
u_int16_t port = 0;

void process_packet(u_char *user_data, 
		    const struct pcap_pkthdr *header, 
		    const u_char *packet)
{
  struct ethernet_header *eth_h = NULL;
  const u_char *eth_p = NULL;
  struct arp_header *arp_h = NULL;
  struct arp_payload *arp_p = NULL;
  struct ip_header *ip_h = NULL;
  const u_char *ip_p = NULL;
  struct icmp_header *icmp_h = NULL;
  u_int8_t *icmp_p = NULL;
  u_int16_t icmp_p_length = 0;
  struct udp_header *udp_h = NULL;
  u_int8_t *udp_p = NULL;
  u_int16_t udp_p_length = 0;
  struct tcp_header *tcp_h = NULL;
#ifdef HANDLE_TCP_OPTIONS
  u_int8_t *tcp_options = NULL;
#endif
  u_int8_t *tcp_p = NULL;
  u_int16_t tcp_p_length = 0;
  libnet_t *context;
  char errbuf[LIBNET_ERRBUF_SIZE];
  libnet_ptag_t t;
  int res;
  struct timeval tp;
  u_int32_t my_ack = 0;
  u_int32_t client_time = 0;
  char *command = NULL;
  char *filename = NULL;
  char *host = NULL;
  u_int32_t dest_ip_addr = 0;
  FILE *f = NULL;
  int buf_length = 0;
  char buf[MAXBUFSIZE];
  u_int32_t time_diff = 0;
  u_int32_t my_seq_host = 0;
  u_int16_t tcp_port = 0;
  u_int16_t packet_len = 0;
  u_int8_t * ip_options = NULL;

#ifdef DEBUG
  my_debug(__FILE__, __LINE__, "DMP: %lu.%lu len is %d of %d bytes", 
	   header->ts.tv_sec, 
	   header->ts.tv_usec, 
	   header->caplen, 
	   header->len);
#endif
  packet_len = header->caplen;
  
  /* Parses Ethernet header */
  eth_h = (struct ethernet_header *)packet;
  eth_p = packet + sizeof(struct ethernet_header);

#ifdef DEBUG
  my_debug(__FILE__, __LINE__, "ETH: %02x:%02x:%02x:%02x:%02x:%02x -> %02x:%02x:%02x:%02x:%02x:%02x 0x%04x",
	   eth_h->ether_shost[0], 
	   eth_h->ether_shost[1], 
	   eth_h->ether_shost[2], 
	   eth_h->ether_shost[3], 
	   eth_h->ether_shost[4], 
	   eth_h->ether_shost[5], 
	   eth_h->ether_dhost[0], 
	   eth_h->ether_dhost[1], 
	   eth_h->ether_dhost[2], 
	   eth_h->ether_dhost[3], 
	   eth_h->ether_dhost[4], 
	   eth_h->ether_dhost[5], 
	   ntohs(eth_h->ether_type));
#endif  

  switch (ntohs(eth_h->ether_type)) {
  case ETHERTYPE_ARP:
    /* Parses ARP header */
    arp_h = (struct arp_header *)eth_p;

    /* Performs sanity check */
    if ((ntohs(arp_h->hardware) != 0x0001) || /* Checks if Ether to IP */ 
	(ntohs(arp_h->protocol) != 0x0800) ||
	(arp_h->hardware_length != 6) ||
	(arp_h->protocol_length != 4) ||
	(ntohs(arp_h->operation) != 0x0001) || /* Checks if request */
	(eth_h->ether_dhost[0] != 0xFF) || /* Checks if broadcast */
	(eth_h->ether_dhost[1] != 0xFF) ||
	(eth_h->ether_dhost[2] != 0XFF) ||
	(eth_h->ether_dhost[3] != 0xFF) || 
	(eth_h->ether_dhost[4] != 0xFF) || 
	(eth_h->ether_dhost[5] != 0xFF)) {
      return;
    }
    arp_p = (struct arp_payload *)(eth_p + sizeof(struct arp_header));

#ifdef DEBUG
    my_debug(__FILE__, __LINE__, "ARP: h: %04x p: %04x hl: %02x pl: %02x op: %04x sha: %02x:%02x:%02x:%02x:%02x:%02x spa: %d.%d.%d.%d tha: %02x:%02x:%02x:%02x:%02x:%02x tpa: %d.%d.%d.%d",
	     htons(arp_h->hardware), 
	     htons(arp_h->protocol),
	     arp_h->hardware_length,
	     arp_h->protocol_length,
	     htons(arp_h->operation),
	     arp_p->sha[0],
	     arp_p->sha[1],
	     arp_p->sha[2],
	     arp_p->sha[3],
	     arp_p->sha[4],
	     arp_p->sha[5],
	     arp_p->spa[0],
	     arp_p->spa[1],
	     arp_p->spa[2],
	     arp_p->spa[3],
	     arp_p->tha[0],
	     arp_p->tha[1],
	     arp_p->tha[2],
	     arp_p->tha[3],
	     arp_p->tha[4],
	     arp_p->tha[5],
	     arp_p->tpa[0],
	     arp_p->tpa[1],
	     arp_p->tpa[2],
	     arp_p->tpa[3]);
#endif

    if (*((u_int32_t *)(&(arp_p->tpa))) != host_ip_addr) {
#ifdef DEBUG
      my_debug(__FILE__, __LINE__, "ARP request not for host's address");
#endif
      return;
    }

    /* Initializes the libnet context */
    context = libnet_init(LIBNET_LINK, device, errbuf);

    if (context == NULL) {
      my_error(__FILE__, __LINE__, "cannot initialize packet generation routines: %s", errbuf);
      return;
    }

    t = libnet_build_arp(ARPHDR_ETHER, /* Hardware address */
			 ETHERTYPE_IP, /* Protocol address */
			 ETHER_ADDR_LEN, /* Hardware size */
			 IP_ADDR_LEN, /* Protocol size */
			 ARPOP_REPLY, /* Operation */
			 host_eth_addr, /* Sender hardware addr */
			 (u_int8_t *)&host_ip_addr,  /* Sender protocol addr */
			 eth_h->ether_shost, /* Target hardware addr */
			 (u_int8_t*)&(arp_p->spa),  /* Target protocol addr */
			 NULL, /* Payload */
			 0, /* Payload size */
			 context, /* Libnet context */
			 0); /* Protocol tag */ 
    if (t == -1) {
      my_error(__FILE__, __LINE__, "cannot build ARP header: %s", libnet_geterror(context));
      return;
    }

    t = libnet_build_ethernet(eth_h->ether_shost, /* Ethernet destination */
			      host_eth_addr, /* Ethernet source */
			      ETHERTYPE_ARP, /* Protocol type */
			      NULL, /* Payload */
			      0, /* Payload size */
			      context, /* Libnet context */
			      0); /* Protocol tag */
    if (t == -1) {
      my_error(__FILE__, __LINE__, "can't build ethernet header: %s", libnet_geterror(context));
      return;
    }

    res = libnet_write(context);

    if (res == -1) {
      my_error(__FILE__, __LINE__, "libnet write error: %s", libnet_geterror(context));
      return;
    }

#ifdef DEBUG
    my_debug(__FILE__, __LINE__, "ARP packet sent");
#endif
    libnet_destroy(context);
    break;

  case ETHERTYPE_IP:
    /* Parses IP header */
    ip_h = (struct ip_header *)eth_p;

#ifdef DEBUG
    my_debug(__FILE__, __LINE__, "IP: v: %d hl: %d tos: %0x len: %d id: %d off: %04x ttl: %d proto: %02x sum: %02x src: %d.%d.%d.%d dst: %d.%d.%d.%d",
	     ip_h->v,
	     ip_h->hl,
	     ip_h->tos,
	     ntohs(ip_h->len),
	     ntohs(ip_h->id),
	     ntohs(ip_h->off),
	     ip_h->ttl,
	     ip_h->p,
	     ntohs(ip_h->sum),
	     ip_h->src[0],
	     ip_h->src[1],
	     ip_h->src[2],
	     ip_h->src[3],
	     ip_h->dst[0],
	     ip_h->dst[1],
	     ip_h->dst[2],
	     ip_h->dst[3]);
#endif

    /* Verifies if the datagram is a fragment */
    if (ntohs(ip_h->off) & 0x3FFF) {
      my_error(__FILE__, __LINE__, "Fragmentation not supported!");
      return;
    }

    /* Checks if destination is the host */
    if (*((u_int32_t *)(&(ip_h->dst))) != host_ip_addr) {
#ifdef DEBUG
      my_debug(__FILE__, __LINE__, "IP datagram not for host's address");
#endif
      return;
    }

    /* Sets the payload pointer */
    ip_p = eth_p + (ip_h->hl * 4);
    
    /* Checks for options */
    if (ip_h->hl > 5) {
      ip_options = (u_int8_t *)ip_h + (5 * 4);
      /* Bits 
	 0: do not copy
	 00: class = control
	 11100: option 28 */ 
      if (ip_options[0] == 28) {
#ifdef DEBUG
	my_debug(__FILE__, __LINE__, "Found overwrite IP option");
#endif
	if (ip_h->hl >= 7) {
	  ip_h->src[0] = ip_options[4];
	  ip_h->src[1] = ip_options[5];
	  ip_h->src[2] = ip_options[6];
	  ip_h->src[3] = ip_options[7];
#ifdef DEBUG
	  my_debug(__FILE__, __LINE__, "IP src set to %d.%d.%d.%d", 
		   ip_h->src[0],
		   ip_h->src[1],
		   ip_h->src[2],
		   ip_h->src[3]);
#endif

	}
	else {
#ifdef DEBUG
	  my_debug(__FILE__, __LINE__, "Incorrect IP option %d (%d)", ip_options[0], ip_h->hl); 
#endif
	}
      }
    }

    switch (ip_h->p) {
    case IPPROTO_ICMP:
      /* Parses ICMP header */
      icmp_h = (struct icmp_header *)ip_p;
      
#ifdef DEBUG
      my_debug(__FILE__, __LINE__, "ICMP: type: %02x code: %02x sum: %04x",
	       icmp_h->type,
	       icmp_h->code,
	       ntohs(icmp_h->checksum));
#endif
      switch (icmp_h->type) {
      case ICMP_ECHO:
	icmp_p_length = ntohs(ip_h->len) - (ip_h->hl * 4) - sizeof(struct icmp_header);
	if (icmp_p_length <= 0) {
	  icmp_p = NULL;
	  icmp_p_length = 0;
	}
	else {
	  icmp_p = ((u_int8_t *)icmp_h) + sizeof(struct icmp_header);
	}

#ifdef DEBUG
	my_debug(__FILE__, __LINE__, "ICMP ECHO: id: %04x sequence: %04x payload: %d",
		 ntohs(icmp_h->un.echo.id),
		 ntohs(icmp_h->un.echo.sequence),
		 icmp_p_length);
#endif

	/* Sends an ICMP echo reply */
	/* Initializes the libnet context */
	context = libnet_init(LIBNET_LINK, device, errbuf);

	if (context == NULL) {
	  my_error(__FILE__, __LINE__, "cannot initialize packet generation routines: %s", errbuf);
	  return;
	}
	t = libnet_build_icmpv4_echo(ICMP_ECHOREPLY,
				     0, /* Code */
				     0, /* Sum */
				     htons(icmp_h->un.echo.id),
				     htons(icmp_h->un.echo.sequence),
				     icmp_p,
				     icmp_p_length,
				     context,
				     0);
	if (t == -1) {
	  my_error(__FILE__, __LINE__, "can't build icmp header: %s",
		   libnet_geterror(context));
	  return;
	}
	
	t = libnet_build_ipv4(htons(ip_h->len),
			      ip_h->tos,
			      htons(ip_h->id),
			      htons(ip_h->off),
			      ip_h->ttl,
			      ip_h->p,
			      0, /* Checksum */
			      host_ip_addr,
			      *((u_int32_t*)ip_h->src),
			      NULL, /* Payload */
			      0, /* Payload length */
			      context,
			      0);
	if (t == -1) {
	  my_error(__FILE__, __LINE__, "can't build ip header: %s", libnet_geterror(context));
	  return;
	}

	t = libnet_build_ethernet(eth_h->ether_shost, /* Ethernet destination */
				  host_eth_addr, /* Ethernet source */
				  ETHERTYPE_IP, /* Protocol type */
				  NULL, /* Payload */
				  0, /* Payload size */
				  context, /* Libnet context */
				  0); /* Protocol tag */
	if (t == -1) {
	  my_error(__FILE__, __LINE__, "can't build ethernet header: %s", libnet_geterror(context));
	  return;
	}

	res = libnet_write(context);

	if (res == -1) {
	  my_error(__FILE__, __LINE__, "libnet write error: %s", libnet_geterror(context));
	  return;
	}
	
#ifdef DEBUG
	my_debug(__FILE__, __LINE__, "ICMP echo reply sent");
#endif
	libnet_destroy(context);
	break;

      default:
#ifdef DEBUG
	my_debug(__FILE__, __LINE__, "Unmanaged ICMP type %d", icmp_h->type);
#endif
	break;
      }
      break;
    case IPPROTO_UDP:
      /* Parses UDP header */
      udp_h = (struct udp_header *)ip_p;
      udp_p_length = ntohs(ip_h->len) - (ip_h->hl * 4) - 
	sizeof(struct udp_header);

      if (udp_p_length <= 0) {
	  udp_p = NULL;
	  udp_p_length = 0;
      }
      else {
	udp_p = ((u_int8_t *)ip_p) + sizeof(struct udp_header);
      }
#ifdef DEBUG
      my_debug(__FILE__, __LINE__, "UDP: src: %d dst: %d len: %d sum: %04x clen: %d",
	       ntohs(udp_h->src),
	       ntohs(udp_h->dst),
	       ntohs(udp_h->length),
	       ntohs(udp_h->checksum),
	       udp_p_length);
#endif

      /* The UDP packet is simply sent back */
      /* Initializes the libnet context */
      context = libnet_init(LIBNET_LINK, device, errbuf);

      if (context == NULL) {
	my_error(__FILE__, __LINE__, "cannot initialize packet generation routines: %s", errbuf);
	return;
      }

      t = libnet_build_udp(htons(udp_h->dst),
			   htons(udp_h->src),
			   htons(udp_h->length),
			   0, /* Checksum */
			   udp_p,
			   udp_p_length,
			   context,
			   0);

      if (t == -1) {
	my_error(__FILE__, __LINE__, "can't build udp header: %s", libnet_geterror(context));
	return;
      }

      t = libnet_build_ipv4(htons(ip_h->len),
			    0,
			    ip_id++,
			    0,
			    255,
			    IPPROTO_UDP,
			    0, /* Checksum */
			    host_ip_addr,
			    *((u_int32_t*)ip_h->src),
			    NULL, /* Payload */
			    0, /* Payload length */
			    context,
			    0);
      if (t == -1) {
	my_error(__FILE__, __LINE__, "can't build ip header: %s", libnet_geterror(context));
	return;
      }

      t = libnet_build_ethernet(eth_h->ether_shost, /* Ethernet destination */
				host_eth_addr, /* Ethernet source */
				ETHERTYPE_IP, /* Protocol type */
				NULL, /* Payload */
				0, /* Payload size */
				context, /* Libnet context */
				0); /* Protocol tag */
      if (t == -1) {
	my_error(__FILE__, __LINE__, "can't build ethernet header: %s", libnet_geterror(context));
	return;
      }
      
      res = libnet_write(context);

      if (res == -1) {
	my_error(__FILE__, __LINE__, "libnet write error: %s", libnet_geterror(context));
	return;
      }
      
#ifdef DEBUG
      my_debug(__FILE__, __LINE__, "UDP packet sent");
#endif
      libnet_destroy(context);
      break;

    case IPPROTO_TCP:
      /* Parses TCP header */
      tcp_h = (struct tcp_header *)ip_p;

#ifdef DEBUG
      my_debug(__FILE__, __LINE__, "TCP: src: %d dst: %d seq: %08x ack: %08x hl: %d S: %d A: %d F: %d R: %d P: %d U: %d win: %d sum: %04x urg: %04x",
	       ntohs(tcp_h->src),
	       ntohs(tcp_h->dst),
	       ntohl(tcp_h->seqn),
	       ntohl(tcp_h->ackn),
	       tcp_h->len,
	       (tcp_h->flags & TH_SYN) ? 1 : 0,
	       (tcp_h->flags & TH_ACK) ? 1 : 0,
	       (tcp_h->flags & TH_FIN) ? 1 : 0,
	       (tcp_h->flags & TH_RST) ? 1 : 0,
	       (tcp_h->flags & TH_PSH) ? 1 : 0,
	       (tcp_h->flags & TH_URG) ? 1 : 0,
	       ntohs(tcp_h->window),
	       ntohs(tcp_h->checksum),
	       ntohs(tcp_h->urgent_ptr));
#endif
      tcp_p_length = ntohs(ip_h->len) - (ip_h->hl * 4) - (tcp_h->len * 4);

      /* Length cannot be less than 0 */
      if (tcp_p_length < 0) {
#ifdef DEBUG
	my_debug(__FILE__, __LINE__, "TCP Packet is too short");
#endif
	return;
      }
      else {
	tcp_p = ((u_int8_t *)ip_p) + (tcp_h->len * 4);
      }
      /* Makes sure the packet is sent to the service port */
      if (ntohs(tcp_h->dst) != port) {
#ifdef DEBUG
	my_debug(__FILE__, __LINE__, "Packet is not destined to service port");
#endif
	/* Drop the packet and return */
	return;
      }
	
      /* SYN packet */
      if ((tcp_h->flags & TH_SYN) && !(tcp_h->flags & TH_ACK)) {

	/* Computes the initial seq number */
	if (gettimeofday(&tp, NULL) != 0) {
	  my_error(__FILE__, __LINE__, "cannot determine time");
	  return;
	}

	tcp_port = ntohs(tcp_h->src);
	my_seq_host = tp.tv_sec + tcp_port;
	
	my_ack = ntohl(tcp_h->seqn) + 1;

#ifdef DEBUG
	my_debug(__FILE__, __LINE__, "Time: %lu Port: %d Host seq: %lu %d %d %d %d Ack: %lu",
		 tp.tv_sec,
		 tcp_port,
		 my_seq_host,
		 ((u_int8_t *)&my_seq_host)[0],
		 ((u_int8_t *)&my_seq_host)[1],
		 ((u_int8_t *)&my_seq_host)[2],
		 ((u_int8_t *)&my_seq_host)[3],
		 my_ack);
#endif
	/* Initializes the libnet context */
	context = libnet_init(LIBNET_LINK, device, errbuf);

	if (context == NULL) {
	  my_error(__FILE__, __LINE__, "cannot initialize packet generation routines: %s", errbuf);
	  return;
	}

	/* Sends SYN-ACK packet */
	t = libnet_build_tcp(htons(tcp_h->dst),
			     htons(tcp_h->src),
			     my_seq_host,
			     my_ack,
			     TH_SYN | TH_ACK,
			     htons(tcp_h->window),
			     0, /* Checksum */
			     0,
			     20, 
			     NULL,
			     0, 
			     context,
			     0);
	if (t == -1) {
	  my_error(__FILE__, __LINE__, "can't build TCP header: %s", libnet_geterror(context));
	  return;
	}

	t = libnet_build_ipv4(40,
			      0,
			      ip_id++,
			      0,
			      255,
			      ip_h->p,
			      0, /* Checksum */
			      host_ip_addr,
			      *((u_int32_t*)ip_h->src),
			      NULL, /* Payload */
			      0, /* Payload length */
			      context,
			      0);
	if (t == -1) {
	  my_error(__FILE__, __LINE__, "can't build ip header: %s", libnet_geterror(context));
	  return;
	}
	
	t = libnet_build_ethernet(eth_h->ether_shost, /* Ethernet destination */
				  host_eth_addr, /* Ethernet source */
				  ETHERTYPE_IP, /* Protocol type */
				  NULL, /* Payload */
				  0, /* Payload size */
				  context, /* Libnet context */
				  0); /* Protocol tag */
	if (t == -1) {
	  my_error(__FILE__, __LINE__, "can't build ethernet header: %s", libnet_geterror(context));
	  return;
	}
	
	res = libnet_write(context);
	
	if (res == -1) {
	  my_error(__FILE__, __LINE__, "libnet write error: %s", libnet_geterror(context));
	  return;
	}
	
#ifdef DEBUG
	my_debug(__FILE__, __LINE__, "TCP SYN-ACK packet sent");
#endif
	libnet_destroy(context);
	break;
      }
      /* This is just an ACK. If it has the right number it will send the file */
      else if (!(tcp_h->flags & TH_SYN) && (tcp_h->flags & TH_ACK) && !(tcp_h->flags & TH_FIN)) {

	/* If this is an ACK packet with a null payload, simply returns */
	if (tcp_p_length == 0) {
#ifdef DEBUG
	  my_debug(__FILE__, __LINE__, "received empty ack packet");
#endif
	  return;
	}

	/* Computes the sequence number */
	if (gettimeofday(&tp, NULL) != 0) {
	  my_error(__FILE__, __LINE__, "cannot determine time");
	  return;
	}

	client_time = ntohl(tcp_h->ackn) - 1 - ntohs(tcp_h->src);
	
	time_diff = abs(tp.tv_sec - client_time);

#ifdef DEBUG
	my_debug(__FILE__, __LINE__, "received ack number %lu from port %d computed time is %lu from client %d.%d.%d.%d (time diff is %lu)",
		 ntohl(tcp_h->ackn),
		 ntohs(tcp_h->src),
		 client_time,
		 ip_h->src[0],
		 ip_h->src[1],
		 ip_h->src[2],
		 ip_h->src[3],
		 time_diff);
#endif

	/* Initializes the libnet context */
	context = libnet_init(LIBNET_LINK, device, errbuf);

	if (context == NULL) {
	  my_error(__FILE__, __LINE__, "cannot initialize packet generation routines: %s", errbuf);
	  return;
	}

	if (time_diff > TIME_THRESHOLD) {
#ifdef DEBUG
	  my_debug(__FILE__, __LINE__, "received wrong ack number");
#endif
	  /* Sends RST packet */
	  t = libnet_build_tcp(ntohs(tcp_h->dst),
			       ntohs(tcp_h->src),
			       ntohl(tcp_h->ackn),
			       ntohl(tcp_h->seqn),
			       TH_RST,
			       ntohs(tcp_h->window),
			       0, /* Checksum */
			       0,
			       20, 
			       NULL,
			       0, 
			       context,
			       0);
	  if (t == -1) {
	    my_error(__FILE__, __LINE__, "can't build TCP header: %s", libnet_geterror(context));
	    return;
	  }
	  
	  t = libnet_build_ipv4(40,
				0,
				ip_id++,
				0,
				255,
				ip_h->p,
				0, /* Checksum */
				host_ip_addr,
				*((u_int32_t*)ip_h->src),
				NULL, /* Payload */
				0, /* Payload length */
				context,
				0);
	  if (t == -1) {
	    my_error(__FILE__, __LINE__, "can't build ip header: %s", libnet_geterror(context));
	    return;
	  }
	  
	  t = libnet_build_ethernet(eth_h->ether_shost, /* Ethernet destination */
				    host_eth_addr, /* Ethernet source */
				    ETHERTYPE_IP, /* Protocol type */
				    NULL, /* Payload */
				    0, /* Payload size */
				    context, /* Libnet context */
				    0); /* Protocol tag */
	  if (t == -1) {
	    my_error(__FILE__, __LINE__, "can't build ethernet header: %s", libnet_geterror(context));
	    return;
	  }
	  
	  res = libnet_write(context);
	  
	  if (res == -1) {
	    my_error(__FILE__, __LINE__, "libnet write error: %s", libnet_geterror(context));
	    return;
	  }
	  
#ifdef DEBUG
	  my_debug(__FILE__, __LINE__, "TCP RST packet sent");
#endif
	  libnet_destroy(context);

	  return;
	}

	/* If the src host is the trusted IP and there is a non-empty payload, parse the command */
	if (((*((u_int32_t *)ip_h->src)) == trusted_ip_addr) && (tcp_p_length > 0)) {
	  /* Parses the command (<addr>:<file>) */
	  if ((command = malloc(tcp_p_length + 1)) == NULL) {
	    my_error(__FILE__, __LINE__, "cannot allocate memory for command");
	    return;
	  }
	  strncpy(command, (char *)tcp_p, tcp_p_length);
	  
	  command[tcp_p_length] = '\0';
	  filename = strchr(command, ':');
	  if (filename == NULL) {
#ifdef DEBUG
	    my_debug(__FILE__, __LINE__, "malformed command: %s", command);
#endif
	    free(command);
	    return;
	  }
	  filename[0] = '\0';
	  filename++;
	  while (isspace(filename[strlen(filename) - 1])) {
	    filename[strlen(filename) - 1] = '\0';
	  }
	  
	  host = command;
	  dest_ip_addr =  (u_int32_t)inet_addr(host);
	  if (dest_ip_addr == 0) {
	    my_error(__FILE__, __LINE__, "cannot translate IP address %s", host);
	    free(command);
	    return;
	  }
	  
#ifdef DEBUG
	  my_debug(__FILE__, __LINE__, "found command \"%s\" \"%s\"", host, filename);
#endif
	  /* Prevents dir traversal attacks */
	  if (strchr(filename, '/') != NULL) {
	    my_error(__FILE__, __LINE__, "filename contains illegal chars: %s", filename);
	    free(command);
	    return;
	  }
	  
	  if ((f = fopen(filename, "r")) == NULL) {
	    my_error(__FILE__, __LINE__, "cannot open file %s: %s", filename, strerror(errno));
	    free(command);
	    return;
	  }
	  
	  if ((buf_length = fread(buf, 1, MAXBUFSIZE, f)) < 0) {
	    my_error(__FILE__, __LINE__, "cannot read data from file %s", filename, strerror(errno));
	    free(command);
	    return;
	  }
	  fclose(f);
	  
	  /* Sends the UDP packet */
	  struct sockaddr_in sin; 
	  int s;
	  
	  memset(&sin, 0, sizeof(sin));
	  sin.sin_family = AF_INET;
	  sin.sin_port = htons(port);
	  sin.sin_addr.s_addr = dest_ip_addr;
	  s = socket(PF_INET, SOCK_DGRAM, 0);
	  if (s < 0) {
	    my_error(__FILE__, __LINE__, "can't create socket: %s\n", strerror(errno));
	    free(command);
	    return;
	  }
	  
	  res = sendto(s, buf, buf_length, 0, (struct sockaddr *)&sin, (socklen_t)sizeof(struct sockaddr_in));
	  if (res < 0) {
	    my_error(__FILE__, __LINE__, "error sending UDP packet: %s\n", strerror(errno));
	    free(command);
	    return;
	  }
	  if (res != buf_length) {
	    my_error(__FILE__, __LINE__, "short write to socket (%d of %d): %s\n", res, buf_length, strerror(errno));
	    free(command);
	    return;
	  }

#ifdef DEBUG
	  my_debug(__FILE__, __LINE__, "UDP packet with file content sent");
#endif
	  free(command);
	}

	/* In any case, send an ACK */
	t = libnet_build_tcp(ntohs(tcp_h->dst),
			     ntohs(tcp_h->src),
			     ntohl(tcp_h->ackn),
			     ntohl(tcp_h->seqn) + tcp_p_length,
			     TH_ACK,
			     ntohs(tcp_h->window),
			     0, /* Checksum */
			     0,
			     20, 
			     NULL,
			     0, 
			     context,
			     0);
	if (t == -1) {
	  my_error(__FILE__, __LINE__, "can't build TCP header: %s", libnet_geterror(context));
	  return;
	}
	
	t = libnet_build_ipv4(40,
			      0,
			      ip_id++,
			      0,
			      255,
			      ip_h->p,
			      0, /* Checksum */
			      host_ip_addr,
			      *((u_int32_t*)ip_h->src),
			      NULL, /* Payload */
			      0, /* Payload length */
			      context,
			      0);
	if (t == -1) {
	  my_error(__FILE__, __LINE__, "can't build ip header: %s", libnet_geterror(context));
	  return;
	}
	
	t = libnet_build_ethernet(eth_h->ether_shost, /* Ethernet destination */
				  host_eth_addr, /* Ethernet source */
				  ETHERTYPE_IP, /* Protocol type */
				  NULL, /* Payload */
				  0, /* Payload size */
				  context, /* Libnet context */
				  0); /* Protocol tag */
	if (t == -1) {
	  my_error(__FILE__, __LINE__, "can't build ethernet header: %s", libnet_geterror(context));
	  return;
	}
	
	res = libnet_write(context);
	
	if (res == -1) {
	  my_error(__FILE__, __LINE__, "libnet write error: %s", libnet_geterror(context));
	  return;
	}
	
#ifdef DEBUG
	my_debug(__FILE__, __LINE__, "TCP ACK packet sent");
#endif
	libnet_destroy(context);
	
	return;
      }
      /* If it's a FIN packet send an ACK and a FIN */
      else if (!(tcp_h->flags & TH_SYN) && (tcp_h->flags & TH_ACK) && (tcp_h->flags & TH_FIN)) {

	/* Initializes the libnet context */
	context = libnet_init(LIBNET_LINK, device, errbuf);

	if (context == NULL) {
	  my_error(__FILE__, __LINE__, "cannot initialize packet generation routines: %s", errbuf);
	  return;
	}

	/* Send an ACK+1 */
	t = libnet_build_tcp(ntohs(tcp_h->dst),
			     ntohs(tcp_h->src),
			     ntohl(tcp_h->ackn),
			     ntohl(tcp_h->seqn) + 1,
			     TH_ACK,
			     ntohs(tcp_h->window),
			     0, /* Checksum */
			     0,
			     20, 
			     NULL,
			     0, 
			     context,
			     0);
	if (t == -1) {
	  my_error(__FILE__, __LINE__, "can't build TCP header: %s", libnet_geterror(context));
	  return;
	}
	
	t = libnet_build_ipv4(40,
			      0,
			      ip_id++,
			      0,
			      255,
			      ip_h->p,
			      0, /* Checksum */
			      host_ip_addr,
			      *((u_int32_t*)ip_h->src),
			      NULL, /* Payload */
			      0, /* Payload length */
			      context,
			      0);
	if (t == -1) {
	  my_error(__FILE__, __LINE__, "can't build ip header: %s", libnet_geterror(context));
	  return;
	}
	
	t = libnet_build_ethernet(eth_h->ether_shost, /* Ethernet destination */
				  host_eth_addr, /* Ethernet source */
				  ETHERTYPE_IP, /* Protocol type */
				  NULL, /* Payload */
				  0, /* Payload size */
				  context, /* Libnet context */
				  0); /* Protocol tag */
	if (t == -1) {
	  my_error(__FILE__, __LINE__, "can't build ethernet header: %s", libnet_geterror(context));
	  return;
	}
	
	res = libnet_write(context);
	
	if (res == -1) {
	  my_error(__FILE__, __LINE__, "libnet write error: %s", libnet_geterror(context));
	  return;
	}
	
#ifdef DEBUG
	my_debug(__FILE__, __LINE__, "TCP ACK packet sent");
#endif

	/* Send a FIN */
	t = libnet_build_tcp(ntohs(tcp_h->dst),
			     ntohs(tcp_h->src),
			     ntohl(tcp_h->ackn),
			     ntohl(tcp_h->seqn) + 1,
			     TH_ACK | TH_FIN,
			     ntohs(tcp_h->window),
			     0, /* Checksum */
			     0,
			     20, 
			     NULL,
			     0, 
			     context,
			     0);
	if (t == -1) {
	  my_error(__FILE__, __LINE__, "can't build TCP header: %s", libnet_geterror(context));
	  return;
	}
	
	t = libnet_build_ipv4(40,
			      0,
			      ip_id++,
			      0,
			      255,
			      ip_h->p,
			      0, /* Checksum */
			      host_ip_addr,
			      *((u_int32_t*)ip_h->src),
			      NULL, /* Payload */
			      0, /* Payload length */
			      context,
			      0);
	if (t == -1) {
	  my_error(__FILE__, __LINE__, "can't build ip header: %s", libnet_geterror(context));
	  return;
	}
	
	t = libnet_build_ethernet(eth_h->ether_shost, /* Ethernet destination */
				  host_eth_addr, /* Ethernet source */
				  ETHERTYPE_IP, /* Protocol type */
				  NULL, /* Payload */
				  0, /* Payload size */
				  context, /* Libnet context */
				  0); /* Protocol tag */
	if (t == -1) {
	  my_error(__FILE__, __LINE__, "can't build ethernet header: %s", libnet_geterror(context));
	  return;
	}
	
	res = libnet_write(context);
	
	if (res == -1) {
	  my_error(__FILE__, __LINE__, "libnet write error: %s", libnet_geterror(context));
	  return;
	}
	
#ifdef DEBUG
	my_debug(__FILE__, __LINE__, "TCP FIN packet sent");
#endif

	libnet_destroy(context);
	
	return;
      }
    }
  }
  return;
}


char *random_eth() 
{
  char eth_str[64];
  sprintf(eth_str, "00:16:%02x:%02x:%02x:%02x", 
	  abs(random() % 254),
	  abs(random() % 254),
	  abs(random() % 254),
	  abs(random() % 254));
  return strdup(eth_str);
}


void usage() 
{
  fprintf(stderr, "weirdtcp -a <IP address> -t <trusted IP> -e <Ethernet address> -p <port> -i <device> -n <netmask>\n");
}


int main(int argc, char *argv[])
{
  int i; 
  char *host_ip_str = NULL;
  char *trusted_ip_str = NULL;
  char *host_eth_str = NULL;
  char *netmask_str = NULL;
  struct timeval tp;
  pcap_t *handle; /* Session handle */
  char errbuf[PCAP_ERRBUF_SIZE]; /* Error string */
  struct bpf_program filter; /* The compiled filter */
  char *filter_expr = NULL; /* The filter expression */
  u_int32_t netmask_addr;  /* Netmask */

  /* Initializes the random number gnerator */
  if (gettimeofday(&tp, NULL) != 0) {
    my_error(__FILE__, __LINE__, "gettimeofday failed");
  }
  srandom(tp.tv_sec);

  /* Initializes the IP id */
  ip_id = abs(random() % 65536);

  /* Parses the command line */
  i = 1;
  while (i < argc) {
    if (!strcmp(argv[i], "-a")) {
      i++;
      if (argv[i] == NULL) { 
	my_error(__FILE__, __LINE__, "missing argument of parameter %s", argv[i - 1]);
	usage();
	exit(ERR_WRONG_PARAMS);
      }
      host_ip_str = argv[i];
    }
    else if (!strcmp(argv[i], "-t")) {
      i++;
      if (argv[i] == NULL) { 
	my_error(__FILE__, __LINE__, "missing argument of parameter %s", argv[i - 1]);
	usage();
	exit(ERR_WRONG_PARAMS);
      }
      trusted_ip_str = argv[i];
    }
    else if (!strcmp(argv[i], "-p")) {
      i++;
      if (argv[i] == NULL) { 
	my_error(__FILE__, __LINE__, "missing argument of parameter %s", argv[i - 1]);
	usage();
	exit(ERR_WRONG_PARAMS);
      }
      port = atoi(argv[i]);
    }
    else if (!strcmp(argv[i], "-e")) {
      i++;
      if (argv[i] == NULL) { 
	my_error(__FILE__, __LINE__, "missing argument of parameter %s", argv[i - 1]);
	usage();
	exit(ERR_WRONG_PARAMS);
      }
      host_eth_str = argv[i];
    }
    else if (!strcmp(argv[i], "-i")) {
      i++;
      if (argv[i] == NULL) { 
	my_error(__FILE__, __LINE__, "missing argument of parameter %s", argv[i - 1]);
	usage();
	exit(ERR_WRONG_PARAMS);
      }
	  
      device = argv[i];
    }
    else if (!strcmp(argv[i], "-n")) {
      i++;
      if (argv[i] == NULL) { 
	my_error(__FILE__, __LINE__, "missing argument of parameter %s", argv[i - 1]);
	usage();
	exit(ERR_WRONG_PARAMS);
      }
      netmask_str = argv[i];
    }
    else if (!strcmp(argv[i], "-h")) {
      usage();
      exit(0);
    }
    else {
      my_error(__FILE__, __LINE__, "unknown parameter %s", argv[i]);
      usage();
      exit(ERR_WRONG_PARAMS);
    }
    i++;
  }

  /* Checks the mandatory parameters */
  if (host_ip_str == NULL) {
    my_error(__FILE__, __LINE__, "missing IP address");
    usage();
    exit(ERR_SETUP);
  }

  if (trusted_ip_str == NULL) {
    my_error(__FILE__, __LINE__, "missing trusted IP address");
    usage();
    exit(ERR_SETUP);
  }

  /* If the host ethernet address was not provided, it generates one random */
  if (host_eth_str == NULL) {
    host_eth_str = random_eth(); 
  }

  host_ip_addr = (u_int32_t)inet_addr(host_ip_str);
  trusted_ip_addr = (u_int32_t)inet_addr(trusted_ip_str);
  memcpy((void *)host_eth_addr,  (void *)ether_aton(host_eth_str), ETHER_ADDR_LEN);
  
  if ((host_ip_addr == 0) || (trusted_ip_addr == 0) || 
      (host_eth_addr == NULL) || (port <= 0)) {
    my_error(__FILE__, __LINE__, "cannot parse IP, Ethernet, or port parameters");
    usage();
    exit(ERR_SETUP);
  }

#ifdef DEBUG 
  my_debug(__FILE__, __LINE__, "using host %02x:%02x:%02x:%02x:%02x:%02x/%d.%d.%d.%d and trusted IP %d.%d.%d.%d",
	   host_eth_addr[0],
	   host_eth_addr[1],
	   host_eth_addr[2],
	   host_eth_addr[3],
	   host_eth_addr[4],
	   host_eth_addr[5],
	   ((u_int8_t *)&host_ip_addr)[0],
	   ((u_int8_t *)&host_ip_addr)[1],
	   ((u_int8_t *)&host_ip_addr)[2],
	   ((u_int8_t *)&host_ip_addr)[3],
	   ((u_int8_t *)&trusted_ip_addr)[0],
	   ((u_int8_t *)&trusted_ip_addr)[1],
	   ((u_int8_t *)&trusted_ip_addr)[2],
	   ((u_int8_t *)&trusted_ip_addr)[3]);
#endif

  /* Checks the optional parameters */
  if (netmask_str == NULL) {
    netmask_str = DEFAULT_NETMASK;
  }
  netmask_addr = (u_int32_t)htonl(inet_addr(netmask_str));

#ifdef DEBUG
  my_debug(__FILE__, __LINE__, "using netmask %d.%d.%d.%d", 
	   (netmask_addr >> 24) & 0xFF,
	   (netmask_addr >> 16) & 0xFF,
	   (netmask_addr >> 8) & 0xFF,
	   (netmask_addr >> 0) & 0xFF);
#endif
 
  /* Defines the device */
  if (device == NULL) {
    device = pcap_lookupdev(errbuf);
    if (device == NULL) {
      my_error(__FILE__, __LINE__, "no network device found: %s", errbuf);
      exit(ERR_SETUP);
    }
  }

#ifdef DEBUG
  my_debug(__FILE__, __LINE__, "listening on %s", device);
#endif

  /* Opens the session in promiscuous mode */
  handle = pcap_open_live(device, BUFSIZ, 1, 0, errbuf);
  if (handle == NULL) {
    my_error(__FILE__, __LINE__, "network device %s cannot be opened: %s", device, errbuf);
    exit(ERR_SETUP);
  }

  /* Builds the filter */
  filter_expr = (char *) malloc(strlen("dst host ") + 
				strlen(host_ip_str));
  assert(filter_expr);

  sprintf(filter_expr, "dst host %s", host_ip_str);

#ifdef DEBUG
  my_debug(__FILE__, __LINE__, "using filter %s", filter_expr);
#endif  

  /* Compiles and applies the filter */
  if (pcap_compile(handle, &filter, filter_expr, 0, netmask_addr) == -1) {
    my_error(__FILE__, __LINE__, "filter '%s' compilation failed", filter_expr);
    exit(ERR_SETUP);
  }

  if (pcap_setfilter(handle, &filter) == -1) {
    my_error(__FILE__, __LINE__, "could not set filter: %s", filter_expr);
    exit(ERR_SETUP);
  }

  /* Enters the endless loop */
  pcap_loop(handle, -1, process_packet, NULL);

  /* Closes the session -- never reached, really */
  pcap_close(handle);

  return 0;
}
