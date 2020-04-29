FROM python:3.8.2-slim-buster

WORKDIR /usr/src/app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 8888

CMD ["python", "simulator_frontend.py", "-b", "192.168.187.133", "-f", "0.0.0.0"]
