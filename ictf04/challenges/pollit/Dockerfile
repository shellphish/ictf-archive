# iCTF 2004 — pollit (UN Voting Service)
# Perl CGI application running under Apache. Uses a PostgreSQL/MySQL backend.
#
# Build:  docker build -t ictf04-pollit .
# Run:    docker run -p 8080:80 ictf04-pollit

FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        apache2 \
        libcgi-pm-perl \
        libdbi-perl \
        libdbd-sqlite3-perl \
 && rm -rf /var/lib/apt/lists/*

RUN a2enmod cgi

COPY src/cgi-bin/ /usr/lib/cgi-bin/
COPY src/html/    /var/www/html/
RUN chmod 755 /usr/lib/cgi-bin/*.pl

EXPOSE 80
CMD ["apache2ctl", "-D", "FOREGROUND"]
