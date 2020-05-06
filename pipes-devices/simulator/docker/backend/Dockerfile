FROM python:3.8.2-slim-buster

WORKDIR /usr/src/app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 8887

CMD ["python", "simulator_backend.py", "-f", "192.168.187.133", "-b", "0.0.0.0"]
