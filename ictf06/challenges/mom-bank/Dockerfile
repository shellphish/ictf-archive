# iCTF 2006 — Hillbilly Bank: Main Web Service (mom)
# Original: lighttpd + PHP 5 on Ubuntu
# Build:  docker build -t ictf06-mom-bank .
# Run:    docker run -p 8080:80 ictf06-mom-bank

FROM php:5.6-apache

RUN docker-php-ext-install mysqli pdo pdo_mysql

# The service used lighttpd, but Apache serves the same PHP
COPY src/*.php /var/www/html/
COPY src/*.css /var/www/html/
COPY src/*.conf /etc/

RUN mkdir -p /var/www/html/accounts \
 && chown -R www-data:www-data /var/www/html

EXPOSE 80
