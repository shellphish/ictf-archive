FROM ubuntu:20.04

RUN apt-get update && apt-get install -y python3 python3-pip

WORKDIR /home/chall/service/

COPY ro/requirements.txt ro/requirements.txt
RUN pip install -r ro/requirements.txt

COPY ro ro


CMD ["python3", "ro/manage.py", "runserver", "0.0.0.0:6666"]
