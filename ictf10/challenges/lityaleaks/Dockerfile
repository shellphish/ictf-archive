FROM php:5.6-apache
RUN apt-get update && apt-get install -y \
    mediawiki \
    mariadb-server \
    && rm -rf /var/lib/apt/lists/*

COPY src/LocalSettings.php /etc/mediawiki/LocalSettings.php

EXPOSE 80

# Note: Full setup requires initializing the MySQL database with MediaWiki schema
# and importing the wikidb dump. The LocalSettings.php is provided for reference.
CMD ["apache2-foreground"]
