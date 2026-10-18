FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive
    
RUN apt-get update && apt-get -y install python3 python3-pip imagemagick uuid-runtime
RUN pip3 install flask werkzeug gunicorn
RUN useradd -m --uid 31337 chall

WORKDIR /home/chall/service/
COPY policy.xml /etc/ImageMagick-6/policy.xml

ENTRYPOINT SECRET=`uuidgen` gunicorn -w 2 --chdir /home/chall/service/ro --bind 0.0.0.0:6666 app:app

# CMD ["python3", "/home/chall/service/ro/app.py"]

        