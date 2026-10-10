# iCTF 2008 — mainwebsite
#
# The original service ran on a Debian-based system with Apache2 and PHP 5.
# We use php:5.6-apache as the closest maintained image; actual competition
# used an older PHP 5.x release.
#
# Build:  docker build -t ictf08-mainwebsite .
# Run:    docker run -p 8080:80 ictf08-mainwebsite

FROM php:5.6-apache

# Install MySQL client extension (service uses a MySQL/SQLite backend)
RUN docker-php-ext-install mysqli pdo pdo_mysql

# Copy service source (extracted from iCTF_2008/mainwebsite.tgz)
# Run: tar -xzf ../../iCTF_2008/mainwebsite.tgz -C src/ --strip-components=2
# (strips the leading "shellphish/mainwebsite/" path prefix)
COPY src/ /var/www/html/

# The original service stored user files and ideas in subdirectories
RUN mkdir -p /var/www/html/users /var/www/html/ideas \
 && chown -R www-data:www-data /var/www/html

# Expose HTTP
EXPOSE 80

# Apache is started by the base image CMD
