FROM php:5.6-apache
RUN docker-php-ext-install mysqli
COPY src/cgi-bin/ /var/www/html/cgi-bin/
RUN chown -R www-data:www-data /var/www/html
RUN a2enmod cgi
EXPOSE 80
