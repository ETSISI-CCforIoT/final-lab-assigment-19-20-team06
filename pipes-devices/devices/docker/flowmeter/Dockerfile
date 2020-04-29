FROM python:3.8.2-slim-buster

WORKDIR /usr/src/app

COPY . .

RUN pip install -r requirements.txt

CMD ["python", "flowmeter_client.py"]
