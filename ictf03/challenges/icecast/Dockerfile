FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y \
    icecast2 \
    && rm -rf /var/lib/apt/lists/*

ARG FLAG=ictf2003{icecast_historical}
ARG ICECAST_PASS=hackme

# Write flag as a static file served at http://host:8000/flag
RUN echo -n "${FLAG}" > /usr/share/icecast2/web/flag

# Build the icecast2 config from the template:
# - update paths to match Debian package locations
# - substitute the admin password
COPY src/icecast.xml /tmp/icecast.xml.tmpl
RUN sed \
        "s/##ICECAST_PASSWD##/${ICECAST_PASS}/g; \
         s|/usr/local/share/icecast/web|/usr/share/icecast2/web|g; \
         s|/usr/local/var/log/icecast|/var/log/icecast2|g; \
         s|/usr/local/share/icecast/admin|/usr/share/icecast2/admin|g; \
         s|/usr/local/share/icecast|/usr/share/icecast2|g" \
        /tmp/icecast.xml.tmpl > /etc/icecast2/icecast.xml && \
    rm /tmp/icecast.xml.tmpl

# icecast2 Debian package runs as icecast2 user
RUN chown icecast2:icecast2 /usr/share/icecast2/web/flag

EXPOSE 8000
CMD ["icecast2", "-c", "/etc/icecast2/icecast.xml"]
