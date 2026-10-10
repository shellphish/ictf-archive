dnl Process this file with autoconf to produce a configure script.
AC_INIT(weirdtcp, 1.0, zanardi@shellphish.net)

dnl Initialize automake
AM_INIT_AUTOMAKE(weirdtcp, 1.0)

dnl Checks for programs.
AC_PROG_CC
AC_PROG_INSTALL

dnl Checks for libraries.
AC_CHECK_LIB(pcap, pcap_open_live, , echo "weirdtcp needs libpcap in order to build"; exit 1,)
AC_CHECK_LIB(net, libnet_getdevice, , echo "weirdtcp needs libnet in order to build"; exit 1,)

dnl Checks for header files.
AC_HEADER_STDC
AC_CHECK_HEADERS(stdarg.h varargs.h, break)
AC_CHECK_HEADERS([netinet/ether.h])
# Checks for library functions.
AC_FUNC_VPRINTF

dnl Checks for typedefs, structures, and compiler characteristics.

dnl Checks for library functions.
AC_CONFIG_FILES(Makefile)
AC_OUTPUT
