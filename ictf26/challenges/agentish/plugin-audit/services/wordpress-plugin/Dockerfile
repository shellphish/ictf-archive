# ── WordPress plugin test container ─────────────────────────────────────────
# Pre-builds WordPress + one specific plugin with SQLite (no MySQL needed).
# At runtime: generates a random flag, plants it, then starts Apache.
#
# Build (from challenge root):
#   docker build --build-arg PLUGIN_SLUG=contact-form-7 \
#     -t agentish_plugin-audit_contact-form-7:latest \
#     -f services/wordpress-plugin/Dockerfile .
# ---------------------------------------------------------------------------

FROM php:8.2-apache

# System tools — cached across all 10 plugin builds
RUN apt-get update && apt-get install -y --no-install-recommends \
        wget curl unzip less sqlite3 openssl libsqlite3-dev \
    && docker-php-ext-install pdo_sqlite \
    && a2enmod rewrite \
    && rm -rf /var/lib/apt/lists/*

# WP-CLI
RUN wget -q https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar \
    && chmod +x wp-cli.phar \
    && mv wp-cli.phar /usr/local/bin/wp

# Apache: allow .htaccess overrides
RUN sed -i 's/AllowOverride None/AllowOverride All/g' /etc/apache2/apache2.conf

# Apache: block direct HTTP access to flag files
RUN printf '<FilesMatch "^flag_.*\\.txt$">\n    Require all denied\n</FilesMatch>\n' \
    > /etc/apache2/conf-enabled/protect-flags.conf

RUN echo 'memory_limit = 512M' > /usr/local/etc/php/conf.d/wp-memory.ini

WORKDIR /var/www/html

# Download WordPress core — cached
RUN wp core download --allow-root

# Install SQLite integration plugin — cached
RUN wget -q https://downloads.wordpress.org/plugin/sqlite-database-integration.latest-stable.zip \
    && unzip -q sqlite-database-integration.latest-stable.zip \
         -d wp-content/plugins/ \
    && rm sqlite-database-integration.latest-stable.zip \
    && cp wp-content/plugins/sqlite-database-integration/db.copy wp-content/db.php \
    && mkdir -p wp-content/database

# Create wp-config.php — cached
# Use sed on the sample file to avoid WP-CLI trying to touch the DB at config time
RUN cp wp-config-sample.php wp-config.php \
    && sed -i "s/database_name_here/wordpress/" wp-config.php \
    && sed -i "s/username_here/wordpress/" wp-config.php \
    && sed -i "s/password_here/wordpress/" wp-config.php \
    && sed -i "s/localhost/localhost/" wp-config.php

# Install WordPress core via SQLite — cached
RUN wp core install --allow-root \
    --url=http://localhost \
    --title="CTF Test" \
    --admin_user=admin \
    --admin_password=ictfadmin123 \
    --admin_email=admin@ctf.local \
    --skip-email

# ── Plugin-specific layers (cache breaks here per slug) ──────────────────────
ARG PLUGIN_SLUG=contact-form-7
ENV PLUGIN_SLUG=${PLUGIN_SLUG}
ENV SECRET="7c57fbaf0014c42f0a871393ea32f851"
# Download the target plugin
RUN wp plugin install ${PLUGIN_SLUG} --allow-root 2>/dev/null || true

# Apply vulnerability patches (if any exist for this plugin)
COPY plugin-changes /tmp/plugin-changes
RUN if [ -d "/tmp/plugin-changes/${PLUGIN_SLUG}" ]; then \
        cp -r /tmp/plugin-changes/${PLUGIN_SLUG}/. wp-content/plugins/${PLUGIN_SLUG}/; \
    fi \
    && rm -rf /tmp/plugin-changes

# Activate the plugin
RUN wp plugin activate ${PLUGIN_SLUG} --allow-root 2>/dev/null || true

# Fix permissions
RUN chown -R www-data:www-data /var/www/html

COPY services/wordpress-plugin/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
