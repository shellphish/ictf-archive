FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y \
    apache2 \
    perl \
    libcgi-pm-perl \
    libdbi-perl \
    libdbd-pg-perl \
    postgresql \
    && rm -rf /var/lib/apt/lists/*

RUN a2enmod cgi

ARG FLAG=ictf2003{query_historical}
ARG ADMIN_PASS=admin
ARG DB_PASS=querypass

ENV FLAG_VALUE=${FLAG}
ENV DB_PASS_VALUE=${DB_PASS}

WORKDIR /build
COPY src/ .

# Substitute placeholders into CGI scripts
RUN ADMIN_HASH=$(perl -MDigest::MD5=md5_hex -e "print md5_hex('${ADMIN_PASS}')") && \
    mkdir -p /var/www/cgi-bin/templates && \
    sed "s/##QUERY_DB_PASS##/${DB_PASS}/g" query_extension.pl > /var/www/cgi-bin/query_extension.pl && \
    sed "s/##QUERY_ADMIN_PASS##/${ADMIN_HASH}/g; s/##QUERY_DB_PASS##/${DB_PASS}/g" change.pl > /var/www/cgi-bin/change.pl && \
    chmod 755 /var/www/cgi-bin/query_extension.pl /var/www/cgi-bin/change.pl && \
    cp -r templates/ /var/www/cgi-bin/templates/ && \
    rm -rf /build

RUN echo 'ServerName localhost' >> /etc/apache2/apache2.conf

COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 80
ENTRYPOINT ["/docker-entrypoint.sh"]
