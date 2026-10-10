FROM python:2.7-slim
RUN useradd -u 31337 -ms /bin/bash challenge
WORKDIR /opt/bot
COPY src/bot.py .
EXPOSE 8080
ENV MOTHER_IP=0.0.0.0
ENV MOTHER_PORT=8080
CMD ["python", "bot.py", "-i", "0.0.0.0", "-p", "8080"]
