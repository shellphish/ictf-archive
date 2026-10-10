# iCTF 2008 — financialsite (Financial Network)
#
# Multi-level PHP web application. Each level is served under its own
# VirtualHost or subdirectory. The original system used Apache2 + PHP 5.
#
# Build:  docker build -t ictf08-financialsite .
# Run:    docker run -p 8081:80 ictf08-financialsite

FROM php:5.6-apache

RUN docker-php-ext-install mysqli pdo pdo_mysql

# Copy all levels
# Run: tar -xzf ../../iCTF_2008/financialsite.tgz -C src/ --strip-components=2
COPY src/ /var/www/html/

RUN chown -R www-data:www-data /var/www/html

EXPOSE 80
