# iCTF 2005 — webasstard (Web interface for BRT)
# Web front-end for the Bass Tard Corporation services.
# Includes biometric auth and a static web UI.
#
# Build:  docker build -t ictf0405-webasstard .
# Run:    docker run -p 8080:80 ictf0405-webasstard

FROM php:5.6-apache

COPY src/ /var/www/html/
RUN chown -R www-data:www-data /var/www/html

EXPOSE 80
