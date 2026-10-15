#ifndef ZOCKET_H
#define ZOCKET_H 

#if __STDC__
#  ifndef NOPROTOS
#    define PARAMS(args)      args
#  endif
#endif
#ifndef PARAMS
#  define PARAMS(args)        ()
#endif

extern int 
connectsock PARAMS((const char *host, 
		    const char *service, 
		    const char *transport));

extern int
connectTCP PARAMS((const char *host, const char *service));

extern int
connectUDP PARAMS((const char *host, const char *service));

extern int
passiveTCP PARAMS((const char *service));

extern int
passiveUDP PARAMS((const char *service));

extern char *
getline_nocrlf PARAMS((int s));

#endif /* ZOCKET_H */
