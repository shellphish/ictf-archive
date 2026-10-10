# iCTF 2010 — PerlCGI (S4)
# Original: Perl CGI "txtviewer.pl" text file viewer via Apache 2.0.59
# Extracted from Challenge-SecuriTech.vmdk / SecuriTech_2005/challenge_08_10/

FROM httpd:2.4
RUN apt-get update && apt-get install -y libcgi-pm-perl && rm -rf /var/lib/apt/lists/*
COPY src/txtviewer.pl /usr/local/apache2/cgi-bin/txtviewer.pl
COPY src/htdocs/ /usr/local/apache2/htdocs/
RUN chmod +x /usr/local/apache2/cgi-bin/txtviewer.pl
EXPOSE 80
