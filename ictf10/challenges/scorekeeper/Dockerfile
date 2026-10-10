FROM php:5.6-apache
RUN docker-php-ext-install mysqli
COPY src/*.php src/index.html /var/www/html/
EXPOSE 80
CMD ["apache2-foreground"]
