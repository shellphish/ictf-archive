# iCTF 2010 — BinCGI (S3)
# Original: 32-bit ELF CGI binary "Storm Control Logs viewer" via Apache 2.0.59
# Extracted from Challenge-SecuriTech.vmdk / SecuriTech_2006/challenge_15/

FROM httpd:2.4
RUN dpkg --add-architecture i386 && \
    apt-get update && apt-get install -y libc6-i386 && \
    rm -rf /var/lib/apt/lists/*
COPY src/displ.cgi /usr/local/apache2/cgi-bin/displ.cgi
COPY src/htdocs/ /usr/local/apache2/htdocs/
RUN chmod +x /usr/local/apache2/cgi-bin/displ.cgi
RUN echo "LoadModule cgi_module modules/mod_cgi.so\nOptions +ExecCGI\nAddHandler cgi-script .cgi" >> /usr/local/apache2/conf/httpd.conf
EXPOSE 80
