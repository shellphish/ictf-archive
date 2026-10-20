#include <stdio.h>
#include <assert.h>
#include <string.h>
#include <stdarg.h>
#define VA_START(a, f)        va_start(a, f)
#define VFPRINTF(file, fmt, ap)        vfprintf(file, fmt, ap)
#include "mydiag.h"

void
my_error (char *file, int line, const char *format, ...)
{
  va_list ap;

  assert(file);
  assert(format);

  VA_START(ap, format);
  fprintf(stderr, "%s:%d: ERROR: ", file, line);
  (void)VFPRINTF(stderr, format, ap);
  va_end (ap);
  if (*format) 
    {
      format += strlen(format);
      if (format[-1] != '\n')
	(void)fputc('\n', stderr);
    }

  fflush(stderr);
  return;
}

void
my_warning (char *file, int line, const char *format, ...)
{
  va_list ap;

  assert(file);
  assert(format);

  VA_START(ap, format);
  fprintf(stderr, "%s:%d: WARNING: ", file, line);
  (void)VFPRINTF(stderr, format, ap);
  va_end (ap);
  if (*format) 
    {
      format += strlen(format);
      if (format[-1] != '\n')
	(void)fputc('\n', stderr);
    }

  fflush(stderr);
  return;
}

void
my_debug (char *file, int line, const char *format, ...)
{
  va_list ap;

  assert(file);
  assert(format);

  VA_START(ap, format);
  fprintf(stderr, "%s:%d: DEBUG: ", file, line);
  (void)VFPRINTF(stderr, format, ap); 
  va_end (ap);
  if (*format) 
    {
      format += strlen(format);
      if (format[-1] != '\n')
	(void)fputc('\n', stderr);
    }

  fflush(stderr);
  return;
}
