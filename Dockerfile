FROM python:3.8.5

WORKDIR /app

COPY requirements.txt /app

RUN pip3 install -r /app/requirements.txt

COPY . /app

CMD gunicorn api_yamdb.wsgi:application --bind 0.0.0.0:8000
