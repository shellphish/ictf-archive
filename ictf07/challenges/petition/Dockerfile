FROM python:2.7-slim
RUN apt-get update && apt-get install -y --no-install-recommends apache2 libapache2-mod-python && rm -rf /var/lib/apt/lists/*
COPY src/cgi-bin/ /usr/lib/cgi-bin/
RUN chmod +x /usr/lib/cgi-bin/petition.py
EXPOSE 80
CMD ["apache2ctl", "-D", "FOREGROUND"]
