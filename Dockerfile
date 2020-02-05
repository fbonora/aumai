FROM python:3.7-alpine as base

RUN apk add --no-cache gcc musl-dev python3-dev libffi-dev openssl-dev

WORKDIR /usr/src/app/aumai

COPY requirements.txt .
RUN pip install --no-cache-dir -r ./requirements.txt

RUN apk del gcc musl-dev python3-dev libffi-dev openssl-dev

COPY . .

ENV FLASK_APP aumai

WORKDIR /usr/src/app

CMD [ "flask", "run", "--host=0.0.0.0" ]