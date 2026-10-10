# configure.ac

AC_INIT([secretd], [1.0], [devel@basstard.com])
AC_CONFIG_SRCDIR([src/secretd.cc])
AM_INIT_AUTOMAKE

AC_PROG_CC
AC_PROG_CXX

AC_ARG_ENABLE([pthreads], [AS_HELP_STRING([--enable-pthreads], [Enable threading])])
AC_ARG_ENABLE([debug], [AS_HELP_STRING([--enable-debug], [Enable debugging])])

if test "$enable_debug" = "yes"; then
  CXXFLAGS="$CXXFLAGS -ggdb"
fi

if test "$enable_pthreads" = "yes"; then
  AC_DEFINE([USE_THREADS])
fi
AC_CHECK_LIB([pthread], [pthread_kill])
AC_CHECK_LIB([crypto], [CRYPTO_lock])
AC_CHECK_LIB([ssl], [SSL_free])
AC_CHECK_LIB([db-4.2], [db_create_4002])

AC_CONFIG_FILES([Makefile src/Makefile scripts/Makefile])
AC_OUTPUT

