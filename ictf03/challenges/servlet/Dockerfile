FROM debian:bullseye-slim

# tomcat9 uses javax.servlet.* (Tomcat 10+ uses jakarta.*); bullseye has tomcat9
RUN apt-get update && apt-get install -y \
    tomcat9 \
    openjdk-11-jdk-headless \
    libpostgresql-jdbc-java \
    postgresql \
    python3 \
    && rm -rf /var/lib/apt/lists/*

ARG FLAG=ictf2003{servlet_historical}
ARG PASSWORD=admin
ARG DBPASSWORD=kbpass

# FLAG and DBPASSWORD needed at runtime (DB init in entrypoint)
ENV FLAG_VALUE=${FLAG}
ENV DBPASSWORD_VALUE=${DBPASSWORD}

WORKDIR /build
COPY src/webapp/ webapp/

# Transform password: each char +1 (Admin.java::checkPassword decrements by 1 to compare)
# Substitute @@SERVLET_PASSWORD@@ and @@SERVLET_DBPASSWORD@@ in Java sources
RUN SERVLET_PASS=$(python3 -c "import sys; print(''.join(chr(ord(c)+1) for c in sys.argv[1]))" "${PASSWORD}") && \
    mkdir -p /build/WEB-INF/classes /build/WEB-INF/lib && \
    cp -r webapp/web/WEB-INF/web.xml /build/WEB-INF/ && \
    for f in webapp/src/ctf/*.java; do \
        sed "s/@@SERVLET_PASSWORD@@/${SERVLET_PASS}/g; \
             s/@@SERVLET_DBPASSWORD@@/${DBPASSWORD}/g" "$f" \
            > "/tmp/$(basename $f)"; \
    done && \
    javac \
        -cp /usr/share/java/servlet-api.jar:/usr/share/java/postgresql.jar \
        -d /build/WEB-INF/classes \
        /tmp/*.java && \
    cp /usr/share/java/postgresql.jar /build/WEB-INF/lib/ && \
    jar cf /var/lib/tomcat9/webapps/search.war -C /build . && \
    rm -rf /build /tmp/*.java

COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 8080
ENTRYPOINT ["/docker-entrypoint.sh"]
