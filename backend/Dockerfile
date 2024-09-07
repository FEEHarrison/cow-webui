FROM python:3.10

RUN apt-get update && apt-get upgrade -y


RUN groupadd -g 999 docker && usermod -aG docker root

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5002

CMD ["gunicorn", "--bind", "0.0.0.0:5002", "--log-level", "debug", "--access-logfile", "-", "--error-logfile", "-", "--capture-output", "app:create_app()"]

# CMD ["python", "app.py"]