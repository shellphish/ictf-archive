FROM php:5.6-apache
RUN docker-php-ext-install mysqli
COPY src/cgi-bin/ /var/www/html/cgi-bin/
COPY src/php-include/ /var/www/html/php-include/
RUN ln -s /var/www/html /var/www/html/public_html
RUN chown -R www-data:www-data /var/www/html
RUN a2enmod cgi
EXPOSE 80
