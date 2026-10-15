FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y \
    apache2 \
    perl \
    libcgi-pm-perl \
    && rm -rf /var/lib/apt/lists/*

# Enable CGI module
RUN a2enmod cgi

ARG FLAG=ictf2003{guestbook_historical}
ARG ADMIN_PASS=admin

WORKDIR /build
COPY src/ .

# Substitute flag into guestbook.txt
# Substitute MD5(ADMIN_PASS) into admin scripts
RUN ADMIN_HASH=$(perl -MDigest::MD5=md5_hex -e "print md5_hex('${ADMIN_PASS}')") && \
    sed "s/##GUESTBOOK_FLAG##/${FLAG}/g" guestbook.txt > /var/www/cgi-bin/guestbook.txt && \
    sed "s/##GUESTBOOK_ADMIN_PASS##/${ADMIN_HASH}/g" guestbook_admin.pl > /var/www/cgi-bin/guestbook_admin.pl && \
    sed "s/##GUESTBOOK_ADMIN_PASS##/${ADMIN_HASH}/g" save_messages_admin.pl > /var/www/cgi-bin/save_messages_admin.pl && \
    cp guestbook.pl      /var/www/cgi-bin/guestbook.pl && \
    cp save_message.pl   /var/www/cgi-bin/save_message.pl && \
    cp -r templates/     /var/www/cgi-bin/templates/ && \
    chmod 755 /var/www/cgi-bin/*.pl && \
    chown www-data:www-data /var/www/cgi-bin/guestbook.txt && \
    chmod 644 /var/www/cgi-bin/guestbook.txt && \
    rm -rf /build

# Apache config: ScriptAlias already set in default config;
# ensure CGI scripts have exec permission in cgi-bin
RUN echo 'ServerName localhost' >> /etc/apache2/apache2.conf

EXPOSE 80
CMD ["apache2ctl", "-D", "FOREGROUND"]
