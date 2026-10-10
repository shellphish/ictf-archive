FROM python:3.11-slim
WORKDIR /app
RUN pip install flask --no-cache-dir
COPY app.py .
COPY templates/ templates/
ENV FLAG=ictf{1_th0ught_1t_w4s_h4rd3n3d_but_1t_w4s_3asy}
ENV SECRET_KEY=super_duper_secretly_kept_secret
EXPOSE 5000
CMD ["python", "app.py"]
